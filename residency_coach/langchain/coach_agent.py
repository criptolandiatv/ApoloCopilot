"""
RESIDENCY COACH - LangChain Agent Architecture
Complete AI Coach implementation with memory, tools, and personas
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from enum import Enum

# LangChain imports
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import tool, Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Supabase
from supabase import create_client, Client

# Pydantic for structured outputs
from pydantic import BaseModel, Field


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Model routing
    FAST_MODEL = "gpt-4o-mini"  # For simple tasks
    SMART_MODEL = "claude-sonnet-4-20250514"  # For complex reasoning
    EMBEDDING_MODEL = "text-embedding-3-small"


config = Config()


# =============================================================================
# DATA MODELS
# =============================================================================

class CoachMode(str, Enum):
    BULLET = "bullet"
    DEBRIEFING = "debriefing"
    SHOW_MILHAO = "show_milhao"
    OUTLIER = "outlier"
    VARZEA = "varzea"
    FREE_CHAT = "free_chat"


class TargetExam(str, Enum):
    USP = "USP"
    UNICAMP = "Unicamp"
    ENARE = "ENARE"
    UNIFESP = "UNIFESP"
    OTHER = "Other"


@dataclass
class UserContext:
    user_id: str
    target_exam: TargetExam
    target_year: int
    current_streak: int
    total_betcoins: int
    level: int
    weak_tags: List[str]
    session_questions_count: int
    session_correct_count: int
    last_error_tags: List[str]
    fatigue_level: float  # 0-1, based on session length and error rate


class QuestionAnalysis(BaseModel):
    """Structured output for question analysis"""
    bullet_text: str = Field(description="1-2 line compressed version of the question")
    correct_answer: str = Field(description="The correct answer letter (A, B, C, D, E)")
    explanation: str = Field(description="Tactical explanation of why the answer is correct")
    traps: List[str] = Field(description="Common traps in this question")
    tags: List[str] = Field(description="3-6 specific tags for this question")
    difficulty: float = Field(description="Difficulty from 0.0 to 1.0")
    related_topics: List[str] = Field(description="Related topics to review")


class BetDecision(BaseModel):
    """Structured output for betting decisions"""
    recommended_bet: int = Field(description="Recommended BetCoin amount")
    confidence: str = Field(description="low, medium, or high")
    reasoning: str = Field(description="Why this bet amount")


# =============================================================================
# SUPABASE CLIENT
# =============================================================================

def get_supabase() -> Client:
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


# =============================================================================
# SYSTEM PROMPT LOADER
# =============================================================================

def load_system_prompt() -> str:
    """Load the master system prompt"""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_instruction.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return get_default_system_prompt()


def get_default_system_prompt() -> str:
    return """Você é o COACH R1 - um mentor de elite para residência médica brasileira.

Combine rigor técnico com cultura brasileira natural. Use linguagem de bet (red/green),
faça referências a memes médicos e cultura pop brasileira quando apropriado.

Seja TÁTICO, não enciclopédico. Foco em padrões de erro e como corrigi-los.

Formate respostas com bullets, destaque armadilhas, e sempre extraia tags para o sistema de aprendizado.
"""


# =============================================================================
# TOOLS FOR THE AGENT
# =============================================================================

@tool
def get_user_weak_tags(user_id: str) -> str:
    """
    Retrieve the user's weakest tags (topics they struggle with most).
    Returns a list of tags ordered by priority weight.
    """
    supabase = get_supabase()

    result = supabase.table("user_tag_weights") \
        .select("tag_id, tags(name, slug), error_rate, priority_weight, times_seen") \
        .eq("user_id", user_id) \
        .gte("times_seen", 3) \
        .order("priority_weight", desc=True) \
        .limit(10) \
        .execute()

    if not result.data:
        return "Usuário ainda não tem histórico suficiente de questões."

    weak_tags = []
    for row in result.data:
        tag_name = row.get("tags", {}).get("name", "Unknown")
        error_rate = row.get("error_rate", 0)
        priority = row.get("priority_weight", 1)
        weak_tags.append(f"- {tag_name}: {error_rate*100:.0f}% erro, prioridade {priority:.1f}")

    return "TAGS FRACAS DO USUÁRIO:\n" + "\n".join(weak_tags)


@tool
def get_question_by_tags(tags: List[str], exclude_recent: bool = True) -> str:
    """
    Fetch a question that matches the given tags.
    Prioritizes questions the user hasn't seen recently.
    """
    supabase = get_supabase()

    # Get tag IDs
    tag_result = supabase.table("tags") \
        .select("id") \
        .in_("slug", tags) \
        .execute()

    if not tag_result.data:
        return "Nenhum tag encontrado."

    tag_ids = [t["id"] for t in tag_result.data]

    # Get questions with these tags
    question_result = supabase.table("question_tags") \
        .select("questions(*)") \
        .in_("tag_id", tag_ids) \
        .limit(5) \
        .execute()

    if not question_result.data:
        return "Nenhuma questão encontrada para esses tags."

    # Return first question
    q = question_result.data[0].get("questions", {})
    return json.dumps({
        "id": q.get("id"),
        "bullet": q.get("bullet_text"),
        "options": q.get("options"),
        "difficulty": q.get("difficulty")
    }, ensure_ascii=False)


@tool
def record_answer(user_id: str, question_id: str, selected_answer: str,
                  is_correct: bool, time_taken_seconds: int,
                  betcoins_wagered: int = 0) -> str:
    """
    Record a user's answer to a question and update their tag weights.
    Returns the result and any achievements unlocked.
    """
    supabase = get_supabase()

    # Calculate XP and BetCoins
    xp_earned = 10 if is_correct else 2
    betcoins_won = betcoins_wagered * 2 if is_correct else -betcoins_wagered

    # Insert answer
    answer_data = {
        "user_id": user_id,
        "question_id": question_id,
        "selected_answer": selected_answer,
        "is_correct": is_correct,
        "time_taken_seconds": time_taken_seconds,
        "betcoins_wagered": betcoins_wagered,
        "betcoins_won": betcoins_won,
        "xp_earned": xp_earned
    }

    supabase.table("user_answers").insert(answer_data).execute()

    # Update user stats
    supabase.rpc("award_xp", {"p_user_id": user_id, "p_xp_amount": xp_earned}).execute()

    # Update BetCoins
    if betcoins_won != 0:
        user = supabase.table("users").select("total_betcoins").eq("id", user_id).single().execute()
        new_balance = user.data["total_betcoins"] + betcoins_won

        supabase.table("users").update({"total_betcoins": new_balance}).eq("id", user_id).execute()

        supabase.table("betcoin_transactions").insert({
            "user_id": user_id,
            "amount": betcoins_won,
            "balance_after": new_balance,
            "transaction_type": "question_bet",
            "reference_id": question_id
        }).execute()

    result = {
        "recorded": True,
        "xp_earned": xp_earned,
        "betcoins_change": betcoins_won,
        "message": "🔥 Acertou!" if is_correct else "❌ Errou, mas registrado para revisão."
    }

    return json.dumps(result, ensure_ascii=False)


@tool
def get_exam_profile(exam_name: str) -> str:
    """
    Get the profile of a specific exam (tag distribution, difficulty, etc.).
    Helps calibrate question selection.
    """
    profiles = {
        "USP": {
            "difficulty_avg": 0.75,
            "top_tags": ["clinica_medica", "cirurgia_geral", "trauma_abdominal"],
            "style": "Casos atípicos, raciocínio clínico profundo, muitas pegadinhas",
            "tip": "Foque em diagnóstico diferencial e conduta em casos complexos"
        },
        "Unicamp": {
            "difficulty_avg": 0.65,
            "top_tags": ["pediatria", "gineco_obstetricia", "preventiva"],
            "style": "Questões mais diretas, menos armadilhas",
            "tip": "Domine os protocolos padrão, menos casos atípicos"
        },
        "ENARE": {
            "difficulty_avg": 0.60,
            "top_tags": ["clinica_medica", "cirurgia_geral", "pediatria"],
            "style": "Cobertura ampla, mais conceitual, estilo livro-texto",
            "tip": "Revise fundamentos de todas as grandes áreas"
        }
    }

    profile = profiles.get(exam_name.upper(), profiles["ENARE"])
    return json.dumps(profile, ensure_ascii=False)


@tool
def generate_study_plan(user_id: str, days_until_exam: int) -> str:
    """
    Generate a personalized study plan based on user's weak tags and time available.
    """
    supabase = get_supabase()

    # Get user weak tags
    weak_result = supabase.table("user_tag_weights") \
        .select("tags(name, slug), error_rate, priority_weight") \
        .eq("user_id", user_id) \
        .gte("times_seen", 3) \
        .order("priority_weight", desc=True) \
        .limit(5) \
        .execute()

    weak_tags = [r["tags"]["name"] for r in weak_result.data] if weak_result.data else []

    # Generate plan
    plan = {
        "days_until_exam": days_until_exam,
        "priority_topics": weak_tags[:3] if weak_tags else ["Clínica Médica", "Cirurgia", "Pediatria"],
        "daily_questions_target": max(20, 100 - days_until_exam),
        "weekly_simulados": 2 if days_until_exam > 30 else 3,
        "focus_mode": "intensivo" if days_until_exam < 30 else "equilibrado",
        "recommendation": f"Com {days_until_exam} dias, foque em saturar seus pontos fracos: {', '.join(weak_tags[:3]) if weak_tags else 'ainda coletando dados'}."
    }

    return json.dumps(plan, ensure_ascii=False)


@tool
def get_show_milhao_question(session_id: str, difficulty_level: str) -> str:
    """
    Get the next question for Show do Milhão mode.
    difficulty_level: 'easy', 'medium', 'hard'
    """
    supabase = get_supabase()

    # Map difficulty to range
    difficulty_ranges = {
        "easy": (0.0, 0.4),
        "medium": (0.4, 0.7),
        "hard": (0.7, 1.0)
    }

    low, high = difficulty_ranges.get(difficulty_level, (0.0, 1.0))

    result = supabase.table("questions") \
        .select("id, bullet_text, options, difficulty") \
        .gte("difficulty", low) \
        .lt("difficulty", high) \
        .eq("is_active", True) \
        .limit(1) \
        .execute()

    if not result.data:
        return json.dumps({"error": "Sem questões disponíveis"})

    q = result.data[0]
    return json.dumps({
        "question_id": q["id"],
        "bullet": q["bullet_text"],
        "options": q["options"],
        "difficulty": q["difficulty"]
    }, ensure_ascii=False)


# =============================================================================
# COACH AGENT CLASS
# =============================================================================

class ResidencyCoachAgent:
    """Main agent class that orchestrates the coaching experience"""

    def __init__(self, user_context: Optional[UserContext] = None):
        self.user_context = user_context
        self.mode = CoachMode.FREE_CHAT
        self.memory = ConversationBufferWindowMemory(
            k=20,
            return_messages=True,
            memory_key="chat_history"
        )

        # Initialize models
        self.smart_model = ChatAnthropic(
            model=config.SMART_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0.7,
            max_tokens=4096
        )

        self.fast_model = ChatOpenAI(
            model=config.FAST_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.5
        )

        # Load system prompt
        self.system_prompt = load_system_prompt()

        # Initialize tools
        self.tools = [
            get_user_weak_tags,
            get_question_by_tags,
            record_answer,
            get_exam_profile,
            generate_study_plan,
            get_show_milhao_question
        ]

        # Create agent
        self._create_agent()

    def _create_agent(self):
        """Create the LangChain agent with tools"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._build_system_message()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(
            llm=self.smart_model,
            tools=self.tools,
            prompt=prompt
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def _build_system_message(self) -> str:
        """Build the system message with user context"""
        base = self.system_prompt

        if self.user_context:
            context = f"""

## CONTEXTO DO USUÁRIO ATUAL
- Prova-alvo: {self.user_context.target_exam.value} {self.user_context.target_year}
- Level: {self.user_context.level}
- BetCoins: {self.user_context.total_betcoins}
- Streak: {self.user_context.current_streak} dias
- Tags fracas: {', '.join(self.user_context.weak_tags[:5])}
- Questões na sessão: {self.user_context.session_questions_count}
- Acertos na sessão: {self.user_context.session_correct_count}
- Nível de fadiga: {self.user_context.fatigue_level:.0%}
"""
            base += context

        return base

    def set_mode(self, mode: CoachMode):
        """Change the coaching mode"""
        self.mode = mode

    async def chat(self, message: str) -> str:
        """Process a user message and return the coach's response"""

        # Add mode context to the message if needed
        mode_prefix = ""
        if self.mode == CoachMode.SHOW_MILHAO:
            mode_prefix = "[MODO: SHOW DO MILHÃO] "
        elif self.mode == CoachMode.OUTLIER:
            mode_prefix = "[MODO: OUTLIER - DEEP DIVE] "
        elif self.mode == CoachMode.BULLET:
            mode_prefix = "[MODO: BULLET] "

        full_input = mode_prefix + message

        # Execute agent
        result = await self.agent_executor.ainvoke({
            "input": full_input
        })

        return result["output"]

    def sync_chat(self, message: str) -> str:
        """Synchronous version of chat"""
        mode_prefix = ""
        if self.mode == CoachMode.SHOW_MILHAO:
            mode_prefix = "[MODO: SHOW DO MILHÃO] "
        elif self.mode == CoachMode.OUTLIER:
            mode_prefix = "[MODO: OUTLIER - DEEP DIVE] "
        elif self.mode == CoachMode.BULLET:
            mode_prefix = "[MODO: BULLET] "

        full_input = mode_prefix + message

        result = self.agent_executor.invoke({
            "input": full_input
        })

        return result["output"]


# =============================================================================
# SPECIALIZED CHAINS
# =============================================================================

class QuestionAnalyzer:
    """Chain for analyzing and compressing questions into bullets"""

    def __init__(self):
        self.model = ChatAnthropic(
            model=config.SMART_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=0.3
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um especialista em análise de questões de residência médica.
Sua tarefa é comprimir questões em formato "Bullet" tático e extrair metadados.

REGRAS:
1. bullet_text: 1-2 linhas mantendo apenas triggers diagnósticos essenciais
2. tags: 3-6 tags específicas (nunca genéricas como "medicina")
3. traps: Identifique por que cada distrator parece certo
4. difficulty: 0.0-1.0 baseado em complexidade e taxa de erro esperada

Responda APENAS em JSON válido."""),
            ("human", """Analise esta questão:

ENUNCIADO:
{question_text}

ALTERNATIVAS:
{options}

RESPOSTA CORRETA: {correct_answer}

Forneça a análise estruturada.""")
        ])

        self.chain = self.prompt | self.model | JsonOutputParser()

    def analyze(self, question_text: str, options: Dict[str, str],
                correct_answer: str) -> QuestionAnalysis:
        """Analyze a question and return structured data"""
        result = self.chain.invoke({
            "question_text": question_text,
            "options": json.dumps(options, ensure_ascii=False),
            "correct_answer": correct_answer
        })

        return QuestionAnalysis(**result)


class BetRecommender:
    """Chain for recommending bet amounts based on user confidence and history"""

    def __init__(self):
        self.model = ChatOpenAI(
            model=config.FAST_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.3
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um conselheiro de apostas educacionais (BetCoins).
Recomende valores de aposta baseado no histórico e confiança do usuário.

Regras:
- Nunca recomendar mais de 20% do saldo total
- Se o tema é fraco para o usuário, recomendar aposta baixa
- Se o usuário está em streak, pode ser mais agressivo

Responda em JSON: {{"recommended_bet": N, "confidence": "low/medium/high", "reasoning": "..."}}"""),
            ("human", """CONTEXTO:
- Saldo atual: {balance} BetCoins
- Tema da questão: {topic}
- Histórico no tema: {topic_history}
- Streak atual: {streak} dias
- Dificuldade da questão: {difficulty}

Qual aposta você recomenda?""")
        ])

        self.chain = self.prompt | self.model | JsonOutputParser()

    def recommend(self, balance: int, topic: str, topic_history: Dict,
                  streak: int, difficulty: float) -> BetDecision:
        """Get bet recommendation"""
        result = self.chain.invoke({
            "balance": balance,
            "topic": topic,
            "topic_history": json.dumps(topic_history),
            "streak": streak,
            "difficulty": difficulty
        })

        return BetDecision(**result)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_coach(user_id: str) -> ResidencyCoachAgent:
    """Factory function to create a coach with user context loaded from DB"""
    supabase = get_supabase()

    # Load user data
    user_result = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .single() \
        .execute()

    if not user_result.data:
        # Return coach without context for new users
        return ResidencyCoachAgent()

    user = user_result.data

    # Load weak tags
    weak_tags_result = supabase.table("user_tag_weights") \
        .select("tags(slug)") \
        .eq("user_id", user_id) \
        .order("priority_weight", desc=True) \
        .limit(10) \
        .execute()

    weak_tags = [r["tags"]["slug"] for r in weak_tags_result.data] if weak_tags_result.data else []

    # Create context
    context = UserContext(
        user_id=user_id,
        target_exam=TargetExam(user.get("target_institution", "ENARE")),
        target_year=user.get("target_year", 2026),
        current_streak=user.get("current_streak", 0),
        total_betcoins=user.get("total_betcoins", 100),
        level=user.get("level", 1),
        weak_tags=weak_tags,
        session_questions_count=0,
        session_correct_count=0,
        last_error_tags=[],
        fatigue_level=0.0
    )

    return ResidencyCoachAgent(user_context=context)


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example usage
    coach = ResidencyCoachAgent()

    # Free chat
    response = coach.sync_chat("Me explica apendicite em formato bullet")
    print(response)

    # Set mode and continue
    coach.set_mode(CoachMode.SHOW_MILHAO)
    response = coach.sync_chat("Começar o Show do Milhão com 100 BetCoins")
    print(response)
