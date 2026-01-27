"""
RESIDENCY COACH API
FastAPI backend for the complete coaching system
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from supabase import create_client, Client

# Import our engines
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gamification.engine import (
    BetCoinsEngine, ShowMilhaoEngine, StreakEngine,
    AchievementsEngine, DailyChallengeEngine,
    ShowMilhaoStatus, Lifeline
)
from langchain.coach_agent import create_coach, CoachMode


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


def get_supabase() -> Client:
    """
    Create and return a Supabase client configured with the module's SUPABASE_URL and SUPABASE_KEY.
    
    Returns:
        Client: A Supabase `Client` instance initialized with the configured URL and key.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

# Auth
class UserCreate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    medical_school: Optional[str] = None
    graduation_year: Optional[int] = None
    target_institution: str = "USP"
    target_year: int = 2026


class UserResponse(BaseModel):
    id: str
    email: Optional[str]
    full_name: str
    level: int
    total_xp: int
    total_betcoins: int
    current_streak: int
    target_institution: str


# Questions
class QuestionCreate(BaseModel):
    exam_id: Optional[str] = None
    original_text: str
    bullet_text: str
    options: Dict[str, str]
    correct_answer: str
    debriefing: str
    difficulty: float = Field(ge=0, le=1, default=0.5)
    tags: List[str] = []


class AnswerSubmit(BaseModel):
    question_id: str
    selected_answer: str
    time_taken_seconds: int
    marked_as_doubt: bool = False
    betcoins_wagered: int = 0


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    debriefing: str
    xp_earned: int
    betcoins_change: int
    new_balance: int
    tags_affected: List[str]
    achievements_unlocked: List[Dict]


# Show do Milhão
class ShowMilhaoStart(BaseModel):
    initial_stake: int = 0
    difficulty_mode: str = "classic"


class ShowMilhaoAnswer(BaseModel):
    question_id: str
    selected_answer: str


class LifelineUse(BaseModel):
    lifeline: str  # "50_50", "pular", "universitarios"
    question_id: str


# Chat
class ChatMessage(BaseModel):
    message: str
    mode: str = "free_chat"  # bullet, debriefing, show_milhao, outlier, varzea


# Study
class StudySessionStart(BaseModel):
    session_type: str = "free_practice"
    tag_focus: Optional[List[str]] = None
    question_count_target: Optional[int] = None
    time_limit_minutes: Optional[int] = None


# Weighting Algorithm
class WeightingRequest(BaseModel):
    user_id: str
    target_exam: str = "USP"
    question_count: int = 10


class WeightedQuestion(BaseModel):
    question_id: str
    priority_score: float
    tags: List[str]
    difficulty: float
    reason: str


# =============================================================================
# APP INITIALIZATION
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    """
    Provide the application's lifespan context for FastAPI, emitting startup and shutdown messages to stdout.
    
    Yields control to the application runtime; on startup it prints a startup message, and on shutdown it prints a shutdown message.
    """
    print("🚀 Residency Coach API starting...")
    yield
    # Shutdown
    print("👋 Residency Coach API shutting down...")


app = FastAPI(
    title="Residency Coach API",
    description="Complete API for the Medical Residency Coaching System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH & STATUS
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Return the current service health status and the current UTC timestamp.
    
    Returns:
        dict: A mapping with keys:
            - "status": "healthy"
            - "timestamp": Current UTC time as an ISO 8601 string (UTC).
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/stats")
async def get_system_stats():
    """
    Return aggregate counts for questions, users, tags, and answers submitted today (UTC).
    
    Returns:
        stats (dict): Mapping with keys:
            - total_questions (int): Total number of questions in the system.
            - total_users (int): Total number of users.
            - total_tags (int): Total number of tags.
            - answers_today (int): Number of user answers recorded since the start of the current UTC date.
    """
    supabase = get_supabase()

    # Questions count
    questions = supabase.table("questions").select("id", count="exact").execute()

    # Users count
    users = supabase.table("users").select("id", count="exact").execute()

    # Tags count
    tags = supabase.table("tags").select("id", count="exact").execute()

    # Answers today
    today = datetime.utcnow().date().isoformat()
    answers_today = supabase.table("user_answers") \
        .select("id", count="exact") \
        .gte("answered_at", today) \
        .execute()

    return {
        "total_questions": questions.count,
        "total_users": users.count,
        "total_tags": tags.count,
        "answers_today": answers_today.count
    }


# =============================================================================
# USER ENDPOINTS
# =============================================================================

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """
    Create a new user record in the database and initialize game-related fields.
    
    Parameters:
        user (UserCreate): Payload containing user profile and optional metadata.
    
    Returns:
        dict: The inserted user record as returned by the database, including initialized fields such as `total_betcoins` (100), `level` (1), `total_xp` (0), and `current_streak` (0).
    
    Raises:
        HTTPException: Raised with status 400 if the user could not be created.
    """
    supabase = get_supabase()

    user_data = {
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "medical_school": user.medical_school,
        "graduation_year": user.graduation_year,
        "target_institution": user.target_institution,
        "target_year": user.target_year,
        "total_betcoins": 100,  # Starting bonus
        "level": 1,
        "total_xp": 0,
        "current_streak": 0
    }

    result = supabase.table("users").insert(user_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create user")

    return result.data[0]


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """
    Fetch a user's profile together with their top weak tags and achievement count.
    
    Parameters:
        user_id (str): The user's UUID.
    
    Returns:
        dict: Merged user record with additional fields:
            - weak_tags (list): Up to 5 tag objects (name, slug) with error_rate and priority_weight for tags the user has seen at least 3 times.
            - achievements_count (int): Total number of achievements the user has.
    
    Raises:
        HTTPException: 404 if no user exists with the provided user_id.
    """
    supabase = get_supabase()

    user = supabase.table("users").select("*").eq("id", user_id).single().execute()

    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    # Get weak tags
    weak_tags = supabase.table("user_tag_weights") \
        .select("tags(name, slug), error_rate, priority_weight") \
        .eq("user_id", user_id) \
        .gte("times_seen", 3) \
        .order("priority_weight", desc=True) \
        .limit(5) \
        .execute()

    # Get achievements count
    achievements = supabase.table("user_achievements") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .execute()

    return {
        **user.data,
        "weak_tags": weak_tags.data or [],
        "achievements_count": achievements.count
    }


@app.post("/api/users/{user_id}/daily-login")
async def daily_login(user_id: str):
    """
    Process a user's daily login by updating streaks, awarding the daily betcoin bonus, and checking for newly unlocked achievements.
    
    Returns:
        result (dict): A summary containing:
            - streak: result of the streak check/update (engine-specific streak summary).
            - daily_bonus: result of the daily bonus claim (engine-specific bonus summary).
            - achievements_unlocked: list of newly unlocked achievements (empty list if none).
    """
    streak = StreakEngine(user_id)
    betcoins = BetCoinsEngine(user_id)
    achievements = AchievementsEngine(user_id)

    # Update streak
    streak_result = streak.check_and_update_streak()

    # Claim daily bonus
    bonus_result = betcoins.daily_bonus()

    # Check achievements
    new_achievements = achievements.check_all_achievements()

    return {
        "streak": streak_result,
        "daily_bonus": bonus_result,
        "achievements_unlocked": new_achievements
    }


# =============================================================================
# QUESTION ENDPOINTS
# =============================================================================

@app.get("/api/questions")
async def get_questions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    difficulty_min: float = Query(default=0, ge=0, le=1),
    difficulty_max: float = Query(default=1, ge=0, le=1),
    tags: Optional[str] = None,
    exam_id: Optional[str] = None
):
    """
    Retrieve a paginated list of active questions filtered by difficulty range and optionally by exam, ordered by creation date descending.
    
    @returns List of question records (dict). Each record includes question fields and a `question_tags` relation with `tags` entries containing `name` and `slug`. An empty list is returned when no questions match.
    """
    supabase = get_supabase()

    query = supabase.table("questions") \
        .select("*, question_tags(tags(name, slug))") \
        .gte("difficulty", difficulty_min) \
        .lte("difficulty", difficulty_max) \
        .eq("is_active", True)

    if exam_id:
        query = query.eq("exam_id", exam_id)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return result.data or []


@app.post("/api/questions")
async def create_question(question: QuestionCreate):
    """
    Create a new question record and associate the provided tags with it.
    
    Parameters:
        question (QuestionCreate): Question payload containing fields to insert (exam_id, original_text, bullet_text,
            options, correct_answer, debriefing, difficulty) and a list of tag slugs to link.
    
    Returns:
        dict: The created question row as returned by the database (includes at least the generated `id` and inserted fields).
    
    Raises:
        HTTPException: With status code 400 if the question could not be created.
    """
    supabase = get_supabase()

    # Insert question
    question_data = {
        "exam_id": question.exam_id,
        "original_text": question.original_text,
        "bullet_text": question.bullet_text,
        "options": question.options,
        "correct_answer": question.correct_answer,
        "debriefing": question.debriefing,
        "difficulty": question.difficulty
    }

    result = supabase.table("questions").insert(question_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create question")

    question_id = result.data[0]["id"]

    # Link tags
    for tag_slug in question.tags:
        tag = supabase.table("tags").select("id").eq("slug", tag_slug).single().execute()
        if tag.data:
            supabase.table("question_tags").insert({
                "question_id": question_id,
                "tag_id": tag.data["id"]
            }).execute()

    return result.data[0]


@app.post("/api/questions/{question_id}/answer", response_model=AnswerResponse)
async def submit_answer(question_id: str, answer: AnswerSubmit, user_id: str = Query(...)):
    """
    Handle a user's answer submission for a question and return the resolved outcome.
    
    Records the answer, resolves any wagered betcoins, awards XP, triggers database updates (including tag-weight adjustments via triggers), and evaluates newly unlocked achievements.
    
    Parameters:
        answer (AnswerSubmit): The submitted answer payload containing selected answer, timing, doubt flag, and wagered betcoins.
    
    Returns:
        AnswerResponse: Result of the submission including whether it was correct, the canonical correct answer and debriefing, XP earned, net betcoins change and new balance, affected tag names, and any newly unlocked achievements.
    
    Raises:
        HTTPException: 404 if the question with the given ID is not found.
    """
    supabase = get_supabase()

    # Get question
    question = supabase.table("questions") \
        .select("correct_answer, debriefing") \
        .eq("id", question_id) \
        .single() \
        .execute()

    if not question.data:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = answer.selected_answer.upper() == question.data["correct_answer"].upper()

    # Process bet
    betcoins = BetCoinsEngine(user_id)
    bet_result = betcoins.resolve_bet(
        amount=answer.betcoins_wagered,
        is_correct=is_correct,
        question_id=question_id
    )

    # Record answer (triggers will update tag weights)
    answer_data = {
        "user_id": user_id,
        "question_id": question_id,
        "selected_answer": answer.selected_answer,
        "is_correct": is_correct,
        "time_taken_seconds": answer.time_taken_seconds,
        "marked_as_doubt": answer.marked_as_doubt,
        "betcoins_wagered": answer.betcoins_wagered,
        "betcoins_won": bet_result.amount_change,
        "xp_earned": bet_result.xp_earned
    }

    supabase.table("user_answers").insert(answer_data).execute()

    # Update user stats
    supabase.rpc("award_xp", {"p_user_id": user_id, "p_xp_amount": bet_result.xp_earned}).execute()

    # Get affected tags
    tags = supabase.table("question_tags") \
        .select("tags(name)") \
        .eq("question_id", question_id) \
        .execute()

    tag_names = [t["tags"]["name"] for t in tags.data] if tags.data else []

    # Check achievements
    achievements = AchievementsEngine(user_id)
    new_achievements = achievements.check_all_achievements()

    return AnswerResponse(
        is_correct=is_correct,
        correct_answer=question.data["correct_answer"],
        debriefing=question.data["debriefing"],
        xp_earned=bet_result.xp_earned,
        betcoins_change=bet_result.amount_change,
        new_balance=bet_result.new_balance,
        tags_affected=tag_names,
        achievements_unlocked=new_achievements
    )


# =============================================================================
# WEIGHTING ALGORITHM ENDPOINT (CORE)
# =============================================================================

@app.post("/api/questions/weighted", response_model=List[WeightedQuestion])
async def get_weighted_questions(request: WeightingRequest):
    """
    Compute and return a ranked list of questions scored by user weaknesses, recency, and exam-specific tag weights.
    
    Combines a user's tag priority and error rates with exam-specific tag multipliers and a recency (spaced-repetition) factor to produce a priority score for each question, then returns the top N questions ordered by that score.
    
    Parameters:
        request (WeightingRequest): Request containing:
            - user_id: ID of the user whose tag weights are used.
            - target_exam: Exam slug used to select exam-specific tag multipliers.
            - question_count: Number of top questions to return.
    
    Returns:
        List[dict]: A list of weighted question entries (length <= request.question_count). Each entry contains:
            - question_id (str): Question identifier.
            - priority_score (float): Computed priority score (higher means higher priority).
            - tags (List[str]): Slugs of tags associated with the question.
            - difficulty (float): Question difficulty value.
            - reason (str): Short human-readable reason for the question's selection.
    """
    supabase = get_supabase()

    # Get user tag weights
    user_weights = supabase.table("user_tag_weights") \
        .select("tag_id, tags(slug, name), priority_weight, error_rate, times_seen, last_seen_at") \
        .eq("user_id", request.user_id) \
        .order("priority_weight", desc=True) \
        .execute()

    # Get exam profile weights
    exam_weights = supabase.table("tags") \
        .select("id, slug, usp_weight, unicamp_weight, enare_weight") \
        .execute()

    exam_weight_map = {}
    weight_field = f"{request.target_exam.lower()}_weight"
    for tag in exam_weights.data or []:
        exam_weight_map[tag["id"]] = tag.get(weight_field, 1.0)

    # Build priority map
    tag_priority = {}
    for uw in user_weights.data or []:
        tag_id = uw["tag_id"]
        base_priority = uw["priority_weight"]
        exam_multiplier = exam_weight_map.get(tag_id, 1.0)

        # Spaced repetition factor
        days_since = 30
        if uw.get("last_seen_at"):
            last_seen = datetime.fromisoformat(uw["last_seen_at"].replace("Z", "+00:00"))
            days_since = (datetime.utcnow() - last_seen.replace(tzinfo=None)).days

        recency_factor = 1.0 + (min(days_since, 30) * 0.02)

        final_priority = base_priority * exam_multiplier * recency_factor
        tag_priority[tag_id] = {
            "priority": final_priority,
            "tag_slug": uw["tags"]["slug"],
            "tag_name": uw["tags"]["name"],
            "error_rate": uw["error_rate"]
        }

    # Get questions with their tags
    questions = supabase.table("questions") \
        .select("id, bullet_text, difficulty, question_tags(tag_id, tags(slug, name))") \
        .eq("is_active", True) \
        .limit(200) \
        .execute()

    # Score each question
    scored_questions = []
    for q in questions.data or []:
        q_tags = q.get("question_tags", [])
        if not q_tags:
            continue

        # Calculate question priority based on its tags
        max_priority = 0
        priority_tags = []
        for qt in q_tags:
            tag_id = qt["tag_id"]
            if tag_id in tag_priority:
                tp = tag_priority[tag_id]
                if tp["priority"] > max_priority:
                    max_priority = tp["priority"]
                priority_tags.append(tp["tag_slug"])

        # If no user data, use base difficulty
        if max_priority == 0:
            max_priority = 1.0 + q["difficulty"]

        # Determine reason for selection
        reason = "Nova tag (exploração)"
        if priority_tags:
            reason = f"Tag fraca: {priority_tags[0]}"

        scored_questions.append({
            "question_id": q["id"],
            "priority_score": round(max_priority, 3),
            "tags": [qt["tags"]["slug"] for qt in q_tags],
            "difficulty": q["difficulty"],
            "reason": reason
        })

    # Sort by priority and return top N
    scored_questions.sort(key=lambda x: x["priority_score"], reverse=True)

    return scored_questions[:request.question_count]


# =============================================================================
# SHOW DO MILHÃO ENDPOINTS
# =============================================================================

@app.post("/api/show-milhao/start")
async def start_show_milhao(config: ShowMilhaoStart, user_id: str = Query(...)):
    """
    Create and initialize a Show do Milhão game session for the specified user.
    
    Parameters:
        config (ShowMilhaoStart): Session configuration including `initial_stake` and `difficulty_mode`.
        user_id (str): ID of the user who will own the session (provided as a query parameter).
    
    Returns:
        dict: Session summary containing:
            - session_id (str): Unique identifier for the new session.
            - initial_stake (int): Stake placed at session start.
            - current_pot (int): Current pot value for the session.
            - lifelines_available (List[str]): Lifelines the user can use in the session.
            - message (str): Human-readable startup message.
    """
    show = ShowMilhaoEngine(user_id)
    session = show.start_session(
        initial_stake=config.initial_stake,
        difficulty_mode=config.difficulty_mode
    )

    return {
        "session_id": session.session_id,
        "initial_stake": session.initial_stake,
        "current_pot": session.current_pot,
        "lifelines_available": session.lifelines_available,
        "message": "🎬 Show do Milhão iniciado! Boa sorte!"
    }


@app.get("/api/show-milhao/{session_id}/question")
async def get_show_milhao_question(session_id: str):
    """
    Retrieve the next question for an active Show do Milhão session.
    
    Parameters:
        session_id (str): Identifier of the Show do Milhão session.
    
    Returns:
        dict: The next question payload for the session.
    
    Raises:
        HTTPException: With status 404 if the session is not found.
        HTTPException: With status 400 if there are no more questions or the session has ended.
    """
    # Get session to find user_id
    supabase = get_supabase()
    session = supabase.table("show_milhao_sessions") \
        .select("user_id") \
        .eq("id", session_id) \
        .single() \
        .execute()

    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    show = ShowMilhaoEngine(session.data["user_id"])
    question = show.get_next_question(session_id)

    if not question:
        raise HTTPException(status_code=400, detail="No more questions or session ended")

    return question


@app.post("/api/show-milhao/{session_id}/answer")
async def answer_show_milhao(session_id: str, answer: ShowMilhaoAnswer):
    """
    Submit an answer for the current question in a Show do Milhão session.
    
    Parameters:
    	session_id (str): Identifier of the Show do Milhão session.
    	answer (ShowMilhaoAnswer): Payload containing `question_id` and the user's `selected_answer`.
    
    Returns:
    	result (dict): Outcome of the answer submission, typically including correctness, updated session state (pot/lifelines), rewards or penalties, and any messages for the user.
    
    Raises:
    	HTTPException: 404 if the session with `session_id` is not found.
    """
    supabase = get_supabase()
    session = supabase.table("show_milhao_sessions") \
        .select("user_id") \
        .eq("id", session_id) \
        .single() \
        .execute()

    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    show = ShowMilhaoEngine(session.data["user_id"])
    result = show.answer_question(
        session_id=session_id,
        question_id=answer.question_id,
        selected_answer=answer.selected_answer
    )

    return result


@app.post("/api/show-milhao/{session_id}/lifeline")
async def use_lifeline(session_id: str, lifeline: LifelineUse):
    """
    Apply a lifeline to an active Show do Milhão session.
    
    Parameters:
        session_id (str): Identifier of the show session.
        lifeline (LifelineUse): Object with `lifeline` (one of the Lifeline enum values) and `question_id` to which the lifeline applies.
    
    Returns:
        dict: Result of the lifeline operation containing updated session state and any lifeline-specific effects (e.g., modified question, lifelines remaining, current pot).
    
    Raises:
        HTTPException: 404 if the session does not exist; 400 if the provided lifeline value is invalid.
    """
    supabase = get_supabase()
    session = supabase.table("show_milhao_sessions") \
        .select("user_id") \
        .eq("id", session_id) \
        .single() \
        .execute()

    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    show = ShowMilhaoEngine(session.data["user_id"])

    try:
        lifeline_enum = Lifeline(lifeline.lifeline)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lifeline")

    result = show.use_lifeline(
        session_id=session_id,
        lifeline=lifeline_enum,
        question_id=lifeline.question_id
    )

    return result


@app.post("/api/show-milhao/{session_id}/stop")
async def stop_show_milhao(session_id: str):
    """
    Stop a Show do Milhão session and finalize the user's winnings.
    
    Returns:
        dict: Result object for the stopped session containing the finalized pot, awarded winnings, and any updated session or user state.
    
    Raises:
        HTTPException: with status code 404 if the session_id does not exist.
    """
    supabase = get_supabase()
    session = supabase.table("show_milhao_sessions") \
        .select("user_id") \
        .eq("id", session_id) \
        .single() \
        .execute()

    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    show = ShowMilhaoEngine(session.data["user_id"])
    result = show.stop_and_take(session_id)

    return result


# =============================================================================
# CHAT ENDPOINT
# =============================================================================

@app.post("/api/chat")
async def chat_with_coach(message: ChatMessage, user_id: str = Query(...)):
    """
    Send a user message to the AI coach and return the coach's reply.
    
    Parameters:
        message (ChatMessage): User message payload containing `message` text and `mode`.
        user_id (str): ID of the user sending the message (provided as a query parameter).
    
    Returns:
        dict: {
            "response": str — coach's textual reply,
            "mode": str — the chat mode used (one of the ChatMessage modes)
        }
    
    Raises:
        HTTPException: with status code 500 if an internal error occurs while processing the message.
    """
    try:
        coach = create_coach(user_id)

        # Set mode
        mode_map = {
            "bullet": CoachMode.BULLET,
            "debriefing": CoachMode.DEBRIEFING,
            "show_milhao": CoachMode.SHOW_MILHAO,
            "outlier": CoachMode.OUTLIER,
            "varzea": CoachMode.VARZEA,
            "free_chat": CoachMode.FREE_CHAT
        }
        coach.set_mode(mode_map.get(message.mode, CoachMode.FREE_CHAT))

        response = coach.sync_chat(message.message)

        return {
            "response": response,
            "mode": message.mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# GAMIFICATION ENDPOINTS
# =============================================================================

@app.get("/api/users/{user_id}/betcoins")
async def get_betcoins(user_id: str):
    """
    Retrieve a user's BetCoins balance and recent transactions.
    
    Parameters:
        user_id (str): The identifier of the user whose BetCoins data will be fetched.
    
    Returns:
        dict: A mapping with keys:
            - "balance": current BetCoins balance for the user.
            - "recent_transactions": list of the user's most recent transaction records (up to 10, most recent first).
    """
    betcoins = BetCoinsEngine(user_id)

    return {
        "balance": betcoins.get_balance(),
        "recent_transactions": betcoins.get_transaction_history(limit=10)
    }


@app.get("/api/users/{user_id}/achievements")
async def get_achievements(user_id: str):
    """
    Retrieve the achievements for a user.
    
    Parameters:
        user_id (str): Identifier of the user whose achievements to fetch.
    
    Returns:
        list: A list of achievement records for the user.
    """
    achievements = AchievementsEngine(user_id)
    return achievements.get_user_achievements()


@app.get("/api/users/{user_id}/daily-challenge")
async def get_daily_challenge(user_id: str):
    """
    Fetch the user's daily challenge and its current progress.
    
    Returns:
        A dictionary with the day's challenge details and progress metrics (e.g., objectives, progress percentage, and any related metadata).
    """
    challenge = DailyChallengeEngine(user_id)
    return challenge.get_today_challenge()


@app.get("/api/leaderboard")
async def get_leaderboard(
    metric: str = Query(default="xp", regex="^(xp|streak|accuracy)$"),
    limit: int = Query(default=50, ge=1, le=100)
):
    """
    Return a ranked leaderboard of users sorted by the chosen metric.
    
    Parameters:
        metric (str): Which metric to sort by; must be one of "xp", "streak", or "accuracy".
        limit (int): Maximum number of leaderboard entries to return (1–100).
    
    Returns:
        list[dict]: Ordered list of leaderboard entries. Each entry contains:
            - rank (int): 1-based position in the leaderboard.
            - id (str): User identifier.
            - full_name (str): User's full name.
            - avatar_url (str | None): URL of the user's avatar, if available.
            - medical_school (str | None): User's medical school, if available.
            - level (int): User level.
            - total_xp (int): Total experience points.
            - current_streak (int): Current daily streak count.
            - total_correct (int): Total correct answers.
            - total_questions_answered (int): Total questions answered.
            - accuracy (float): Percentage accuracy computed as (total_correct / total_questions_answered) * 100, rounded to one decimal place (0.0 if no answered questions).
    """
    supabase = get_supabase()

    order_field = {
        "xp": "total_xp",
        "streak": "current_streak",
        "accuracy": "total_correct"
    }[metric]

    result = supabase.table("users") \
        .select("id, full_name, avatar_url, medical_school, level, total_xp, current_streak, total_correct, total_questions_answered") \
        .gte("total_questions_answered", 10) \
        .order(order_field, desc=True) \
        .limit(limit) \
        .execute()

    leaderboard = []
    for i, user in enumerate(result.data or []):
        accuracy = 0
        if user["total_questions_answered"] > 0:
            accuracy = round((user["total_correct"] / user["total_questions_answered"]) * 100, 1)

        leaderboard.append({
            "rank": i + 1,
            **user,
            "accuracy": accuracy
        })

    return leaderboard


# =============================================================================
# TAGS ENDPOINT
# =============================================================================

@app.get("/api/tags")
async def get_tags(category: Optional[str] = None):
    """
    Retrieve all tags, optionally filtering by category.
    
    If a category is provided, only tags with that category value are returned.
    
    Parameters:
        category (str | None): Optional category to filter tags by.
    
    Returns:
        List[dict]: A list of tag records (dictionaries); an empty list if no tags match.
    """
    supabase = get_supabase()

    query = supabase.table("tags").select("*")

    if category:
        query = query.eq("category", category)

    result = query.order("name").execute()
    return result.data or []


@app.get("/api/users/{user_id}/tag-performance")
async def get_tag_performance(user_id: str):
    """
    Retrieve a user's tag performance records ordered by priority weight.
    
    Returns:
        A list of tag-performance records (dictionaries) for the given user where `times_seen` is at least 1, ordered by `priority_weight` descending; an empty list if none are found.
    """
    supabase = get_supabase()

    result = supabase.table("user_tag_weights") \
        .select("*, tags(name, slug, category)") \
        .eq("user_id", user_id) \
        .gte("times_seen", 1) \
        .order("priority_weight", desc=True) \
        .execute()

    return result.data or []


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)