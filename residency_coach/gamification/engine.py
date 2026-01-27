"""
RESIDENCY COACH - Gamification Engine
Complete BetCoins, Show do Milhão, Achievements, and Streak system
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from supabase import create_client, Client


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


def get_supabase() -> Client:
    """
    Create and return a Supabase client configured with the module's SUPABASE_URL and SUPABASE_KEY.
    
    Returns:
        client (Client): A configured Supabase client instance ready for database and auth operations.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# =============================================================================
# DATA MODELS
# =============================================================================

class TransactionType(str, Enum):
    DAILY_BONUS = "daily_bonus"
    STREAK_BONUS = "streak_bonus"
    QUESTION_BET = "question_bet"
    SHOW_MILHAO = "show_milhao"
    CHALLENGE_WIN = "challenge_win"
    ACHIEVEMENT = "achievement"
    REFERRAL = "referral"
    PURCHASE = "purchase"
    ADMIN_GRANT = "admin_grant"


class ShowMilhaoStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


class Lifeline(str, Enum):
    FIFTY_FIFTY = "50_50"
    SKIP = "pular"
    UNIVERSITY = "universitarios"


@dataclass
class BetResult:
    success: bool
    amount_change: int
    new_balance: int
    message: str
    xp_earned: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)


@dataclass
class ShowMilhaoState:
    session_id: str
    current_question: int
    total_questions: int
    current_pot: int
    initial_stake: int
    checkpoints: List[int]
    lifelines_available: Dict[str, bool]
    lifelines_used: List[str]
    questions_answered: List[Dict]
    status: ShowMilhaoStatus


# =============================================================================
# BETCOINS ENGINE
# =============================================================================

class BetCoinsEngine:
    """Manages all BetCoin transactions and balances"""

    def __init__(self, user_id: str):
        """
        Initialize the instance with the target user's identifier and a Supabase client.
        
        Parameters:
            user_id (str): The unique identifier of the user whose data this instance will operate on.
        """
        self.user_id = user_id
        self.supabase = get_supabase()

    def get_balance(self) -> int:
        """
        Return the current BetCoin balance for the engine's user.
        
        Returns:
            int: The user's current BetCoin balance; returns 0 if the balance is not available.
        """
        result = self.supabase.table("users") \
            .select("total_betcoins") \
            .eq("id", self.user_id) \
            .single() \
            .execute()

        return result.data.get("total_betcoins", 0) if result.data else 0

    def _record_transaction(
        self,
        amount: int,
        transaction_type: TransactionType,
        description: str = None,
        reference_id: str = None
    ) -> int:
        """
        Apply a betcoin change for the user and persist a corresponding transaction record.
        
        Parameters:
            amount (int): Change to apply to the user's balance; positive to credit, negative to debit. If the debit would make the balance negative, the amount is adjusted so the balance becomes zero.
            transaction_type (TransactionType): The category of the transaction.
            description (str, optional): Human-readable note about the transaction.
            reference_id (str, optional): External identifier linking this transaction to another entity (e.g., question, session, achievement).
        
        Returns:
            int: The user's updated total betcoins balance after the transaction (always zero or greater).
        """
        current_balance = self.get_balance()
        new_balance = current_balance + amount

        # Prevent negative balance
        if new_balance < 0:
            new_balance = 0
            amount = -current_balance

        # Update user balance
        self.supabase.table("users") \
            .update({"total_betcoins": new_balance, "updated_at": datetime.utcnow().isoformat()}) \
            .eq("id", self.user_id) \
            .execute()

        # Record transaction
        self.supabase.table("betcoin_transactions").insert({
            "user_id": self.user_id,
            "amount": amount,
            "balance_after": new_balance,
            "transaction_type": transaction_type.value,
            "description": description,
            "reference_id": reference_id
        }).execute()

        return new_balance

    def daily_bonus(self) -> BetResult:
        """
        Grant the user's daily login BetCoins bonus if not already claimed today.
        
        If the user has not claimed today's bonus, awards a BetCoins amount computed as 10 plus 2 per day of the user's current streak, capped so the bonus does not exceed 50, records the transaction, and grants 5 XP. If the bonus was already claimed today, no balance change is made.
        
        Returns:
            BetResult: success `True` when a bonus was granted (includes `amount_change`, `new_balance`, `message`, and `xp_earned`); `False` when the bonus was already claimed today (`amount_change` is 0 and `new_balance` reflects the current balance).
        """
        # Check if already claimed today
        today = datetime.utcnow().date().isoformat()

        existing = self.supabase.table("betcoin_transactions") \
            .select("id") \
            .eq("user_id", self.user_id) \
            .eq("transaction_type", TransactionType.DAILY_BONUS.value) \
            .gte("created_at", today) \
            .execute()

        if existing.data:
            return BetResult(
                success=False,
                amount_change=0,
                new_balance=self.get_balance(),
                message="Bonus diário já coletado hoje!"
            )

        # Award bonus (base 10 + streak bonus)
        user = self.supabase.table("users") \
            .select("current_streak") \
            .eq("id", self.user_id) \
            .single() \
            .execute()

        streak = user.data.get("current_streak", 0) if user.data else 0
        bonus_amount = 10 + min(streak * 2, 40)  # Max 50 from streak

        new_balance = self._record_transaction(
            amount=bonus_amount,
            transaction_type=TransactionType.DAILY_BONUS,
            description=f"Daily bonus (streak: {streak})"
        )

        return BetResult(
            success=True,
            amount_change=bonus_amount,
            new_balance=new_balance,
            message=f"🎁 Bonus diário: +{bonus_amount} BetCoins! (Streak: {streak} dias)",
            xp_earned=5
        )

    def place_bet(self, amount: int, question_id: str) -> Tuple[bool, int]:
        """
        Compute the allowed bet amount for a question by enforcing the user's balance and a maximum of 50% of the balance.
        
        Parameters:
            amount (int): Desired bet amount.
            question_id (str): Identifier of the question (not used for calculation).
        
        Returns:
            tuple: (success (bool), bet_amount (int)) — `success` is `True` when the bet is accepted; `bet_amount` is the adjusted amount (0 if `amount` <= 0).
        """
        balance = self.get_balance()

        if amount <= 0:
            return True, 0

        if amount > balance:
            amount = balance  # Bet max available

        if amount > balance * 0.5:
            amount = int(balance * 0.5)  # Cap at 50% of balance

        return True, amount

    def resolve_bet(self, amount: int, is_correct: bool, question_id: str) -> BetResult:
        """
        Settle a question bet and apply the resulting balance change for the user.
        
        Parameters:
            amount (int): The bet amount placed for the question; values <= 0 are treated as no bet.
            is_correct (bool): Whether the user's answer was correct.
            question_id (str): Identifier of the question used as a transaction reference.
        
        Returns:
            BetResult: Result of settling the bet including:
                - `amount_change`: positive amount awarded on win (twice the bet), negative amount on loss, or 0 if no bet.
                - `new_balance`: user's balance after the transaction (unchanged for no bet).
                - `message`: user-facing summary of the outcome.
                - `xp_earned`: experience points awarded (varies by outcome).
        """
        if amount <= 0:
            return BetResult(
                success=True,
                amount_change=0,
                new_balance=self.get_balance(),
                message="Sem aposta nesta questão.",
                xp_earned=10 if is_correct else 2
            )

        if is_correct:
            # Win: get 2x the bet
            winnings = amount * 2
            new_balance = self._record_transaction(
                amount=winnings,
                transaction_type=TransactionType.QUESTION_BET,
                description=f"Bet win: {amount} -> {winnings}",
                reference_id=question_id
            )
            return BetResult(
                success=True,
                amount_change=winnings,
                new_balance=new_balance,
                message=f"🎰 GANHOU! +{winnings} BetCoins (aposta: {amount})",
                xp_earned=15
            )
        else:
            # Lose: lose the bet
            new_balance = self._record_transaction(
                amount=-amount,
                transaction_type=TransactionType.QUESTION_BET,
                description=f"Bet loss: -{amount}",
                reference_id=question_id
            )
            return BetResult(
                success=True,
                amount_change=-amount,
                new_balance=new_balance,
                message=f"📉 Perdeu {amount} BetCoins. Mas o aprendizado fica!",
                xp_earned=5
            )

    def get_transaction_history(self, limit: int = 20) -> List[Dict]:
        """
        Retrieve the user's most recent betcoin transaction records.
        
        Parameters:
            limit (int): Maximum number of transactions to return (default 20).
        
        Returns:
            List[Dict]: A list of transaction records sorted by newest first; empty list if none found.
        """
        result = self.supabase.table("betcoin_transactions") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return result.data if result.data else []


# =============================================================================
# SHOW DO MILHÃO ENGINE
# =============================================================================

class ShowMilhaoEngine:
    """Manages Show do Milhão game sessions"""

    # Prize ladder (classic format)
    PRIZE_LADDER = [
        100,    # Q1
        200,    # Q2
        300,    # Q3
        500,    # Q4
        1000,   # Q5 - CHECKPOINT 1
        2000,   # Q6
        4000,   # Q7
        8000,   # Q8
        16000,  # Q9
        32000,  # Q10 - CHECKPOINT 2
        64000,  # Q11
        125000, # Q12
        250000, # Q13
        500000, # Q14
        1000000 # Q15 - MILLION!
    ]

    CHECKPOINTS = [5, 10]  # Safe points (0-indexed: Q5 and Q10)

    def __init__(self, user_id: str):
        """
        Initialize the engine with the given user context and related services.
        
        Parameters:
            user_id (str): The identifier of the user the engine will operate for. Initializes a Supabase client and a BetCoinsEngine instance bound to this user.
        """
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def start_session(
        self,
        initial_stake: int = 0,
        difficulty_mode: str = "classic"
    ) -> ShowMilhaoState:
        """
        Start a new Show do Milhão game session for the user.
        
        Creates and persists a new session record, optionally deducting an initial stake (capped to the user's available balance), and returns the initial session state.
        
        Parameters:
            initial_stake (int): Amount of BetCoins to wager as the session entry stake; if greater than the user's balance, the stake is reduced to the available balance.
            difficulty_mode (str): Difficulty progression mode for the session (e.g., "classic").
        
        Returns:
            ShowMilhaoState: The newly created session state including session_id, current_question (0), total_questions (15), current_pot (equal to the final applied stake), initial_stake, checkpoints, available/used lifelines, questions_answered (empty), and status set to IN_PROGRESS.
        """

        # Deduct initial stake if any
        if initial_stake > 0:
            balance = self.betcoins.get_balance()
            if initial_stake > balance:
                initial_stake = balance

            self.betcoins._record_transaction(
                amount=-initial_stake,
                transaction_type=TransactionType.SHOW_MILHAO,
                description="Show do Milhão entry stake"
            )

        session_id = str(uuid4())

        # Create session in DB
        session_data = {
            "id": session_id,
            "user_id": self.user_id,
            "total_questions": 15,
            "difficulty_progression": difficulty_mode,
            "current_question": 0,
            "initial_betcoins": initial_stake,
            "current_pot": initial_stake,
            "checkpoints": self.CHECKPOINTS,
            "lifelines_available": {
                "50_50": True,
                "pular": True,
                "universitarios": True
            },
            "lifelines_used": [],
            "questions_answered": [],
            "status": ShowMilhaoStatus.IN_PROGRESS.value
        }

        self.supabase.table("show_milhao_sessions").insert(session_data).execute()

        return ShowMilhaoState(
            session_id=session_id,
            current_question=0,
            total_questions=15,
            current_pot=initial_stake,
            initial_stake=initial_stake,
            checkpoints=self.CHECKPOINTS,
            lifelines_available=session_data["lifelines_available"],
            lifelines_used=[],
            questions_answered=[],
            status=ShowMilhaoStatus.IN_PROGRESS
        )

    def get_session(self, session_id: str) -> Optional[ShowMilhaoState]:
        """
        Retrieve the Show do Milhão session state for the given session ID.
        
        Parameters:
            session_id (str): Identifier of the session to fetch.
        
        Returns:
            ShowMilhaoState or None: The session state if found, otherwise None.
        """
        result = self.supabase.table("show_milhao_sessions") \
            .select("*") \
            .eq("id", session_id) \
            .single() \
            .execute()

        if not result.data:
            return None

        s = result.data
        return ShowMilhaoState(
            session_id=s["id"],
            current_question=s["current_question"],
            total_questions=s["total_questions"],
            current_pot=s["current_pot"],
            initial_stake=s["initial_betcoins"],
            checkpoints=s["checkpoints"],
            lifelines_available=s["lifelines_available"],
            lifelines_used=s["lifelines_used"],
            questions_answered=s["questions_answered"],
            status=ShowMilhaoStatus(s["status"])
        )

    def get_next_question(self, session_id: str) -> Optional[Dict]:
        """
        Selects and returns the next active question for a running Show do Milhão session.
        
        Parameters:
            session_id (str): Identifier of the Show do Milhão session.
        
        Returns:
            dict or None: A mapping with the next question and session context, or `None` if the session is missing, not in progress, or no eligible question is available. When present, the dict contains:
                - question_id (str): The question's unique identifier.
                - question_number (int): 1-based index of this question within the session.
                - total_questions (int): Total number of questions in the session (typically 15).
                - bullet (str): The question text or prompt.
                - options (dict): Answer options keyed by option identifier.
                - difficulty (float): Question difficulty score.
                - prize_if_correct (int): BetCoins awarded for answering this question correctly.
                - current_pot (int): Current accumulated pot for the session.
                - is_checkpoint (bool): Whether this question position is a guaranteed checkpoint.
                - lifelines_available (dict): Lifelines still available to the user for the session.
        """
        state = self.get_session(session_id)
        if not state or state.status != ShowMilhaoStatus.IN_PROGRESS:
            return None

        # Determine difficulty based on question number
        q_num = state.current_question
        if q_num < 5:
            difficulty_range = (0.0, 0.4)  # Easy
        elif q_num < 10:
            difficulty_range = (0.4, 0.7)  # Medium
        else:
            difficulty_range = (0.7, 1.0)  # Hard

        # Get already answered question IDs
        answered_ids = [q["question_id"] for q in state.questions_answered]

        # Fetch a question
        query = self.supabase.table("questions") \
            .select("id, bullet_text, options, correct_answer, difficulty") \
            .gte("difficulty", difficulty_range[0]) \
            .lt("difficulty", difficulty_range[1]) \
            .eq("is_active", True)

        if answered_ids:
            query = query.not_.in_("id", answered_ids)

        result = query.limit(10).execute()

        if not result.data:
            return None

        # Pick random from results
        question = random.choice(result.data)

        return {
            "question_id": question["id"],
            "question_number": q_num + 1,
            "total_questions": 15,
            "bullet": question["bullet_text"],
            "options": question["options"],
            "difficulty": question["difficulty"],
            "prize_if_correct": self.PRIZE_LADDER[q_num],
            "current_pot": state.current_pot,
            "is_checkpoint": q_num in self.CHECKPOINTS,
            "lifelines_available": state.lifelines_available
        }

    def answer_question(
        self,
        session_id: str,
        question_id: str,
        selected_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a submitted answer for a Show do Milhão session and advance or finalize the session accordingly.
        
        Parameters:
            session_id (str): ID of the Show do Milhão session.
            question_id (str): ID of the question being answered.
            selected_answer (str): The user's selected answer identifier/value.
        
        Returns:
            dict: Result payload describing the outcome. Possible structures:
              - Error: {"error": "<message>"} when session is inactive or question not found.
              - WINNER: {
                    "result": "WINNER",
                    "is_correct": True,
                    "correct_answer": str,
                    "prize_won": int,            # final pot awarded
                    "message": str,
                    "debriefing": Optional[str]
                }
              - CORRECT (advance to next question): {
                    "result": "CORRECT",
                    "is_correct": True,
                    "correct_answer": str,
                    "current_pot": int,         # updated pot after prize
                    "next_question": int,       # next question index (1-based)
                    "is_checkpoint": bool,
                    "message": str,
                    "debriefing": Optional[str]
                }
              - WRONG (session ends): {
                    "result": "WRONG",
                    "is_correct": False,
                    "correct_answer": str,
                    "final_prize": int,         # prize preserved by last checkpoint (0 if none)
                    "pot_lost": int,            # amount lost from current pot
                    "message": str,
                    "debriefing": Optional[str]
                }
        """
        state = self.get_session(session_id)
        if not state or state.status != ShowMilhaoStatus.IN_PROGRESS:
            return {"error": "Session not active"}

        # Get correct answer
        question = self.supabase.table("questions") \
            .select("correct_answer, debriefing") \
            .eq("id", question_id) \
            .single() \
            .execute()

        if not question.data:
            return {"error": "Question not found"}

        correct_answer = question.data["correct_answer"]
        is_correct = selected_answer.upper() == correct_answer.upper()

        q_num = state.current_question
        prize = self.PRIZE_LADDER[q_num]

        # Record answer
        answer_record = {
            "question_id": question_id,
            "question_number": q_num + 1,
            "selected": selected_answer,
            "correct": correct_answer,
            "is_correct": is_correct,
            "prize": prize if is_correct else 0
        }
        state.questions_answered.append(answer_record)

        if is_correct:
            # Advance to next question
            new_pot = state.current_pot + prize
            new_question = q_num + 1

            if new_question >= 15:
                # WON THE MILLION!
                self._end_session(session_id, ShowMilhaoStatus.WON, new_pot, state.questions_answered)
                return {
                    "result": "WINNER",
                    "is_correct": True,
                    "correct_answer": correct_answer,
                    "prize_won": new_pot,
                    "message": f"🏆 VOCÊ VENCEU O SHOW DO MILHÃO! +{new_pot} BetCoins!",
                    "debriefing": question.data.get("debriefing")
                }
            else:
                # Continue
                self.supabase.table("show_milhao_sessions").update({
                    "current_question": new_question,
                    "current_pot": new_pot,
                    "questions_answered": state.questions_answered
                }).eq("id", session_id).execute()

                is_checkpoint = q_num in self.CHECKPOINTS

                return {
                    "result": "CORRECT",
                    "is_correct": True,
                    "correct_answer": correct_answer,
                    "current_pot": new_pot,
                    "next_question": new_question + 1,
                    "is_checkpoint": is_checkpoint,
                    "message": f"✅ CORRETO! +{prize} | Pot: {new_pot} BetCoins" +
                              (" | 🏁 CHECKPOINT ATINGIDO!" if is_checkpoint else ""),
                    "debriefing": question.data.get("debriefing")
                }
        else:
            # WRONG - Game over
            # Calculate final prize (fall to last checkpoint)
            final_prize = 0
            for cp in reversed(self.CHECKPOINTS):
                if cp < q_num:
                    final_prize = self.PRIZE_LADDER[cp]
                    break

            self._end_session(session_id, ShowMilhaoStatus.LOST, final_prize, state.questions_answered)

            return {
                "result": "WRONG",
                "is_correct": False,
                "correct_answer": correct_answer,
                "final_prize": final_prize,
                "pot_lost": state.current_pot - final_prize,
                "message": f"❌ ERROU! Resposta correta: {correct_answer}. " +
                          (f"Você leva {final_prize} BetCoins (último checkpoint)." if final_prize > 0
                           else "Você perde tudo. Mas o conhecimento fica!"),
                "debriefing": question.data.get("debriefing")
            }

    def use_lifeline(self, session_id: str, lifeline: Lifeline, question_id: str) -> Dict:
        """
        Apply a lifeline to the specified Show do Milhão session question and return its outcome.
        
        Parameters:
            session_id (str): ID of the active show session.
            lifeline (Lifeline): The lifeline to use (FIFTY_FIFTY, SKIP, or UNIVERSITY).
            question_id (str): ID of the question the lifeline is applied to.
        
        Returns:
            dict: On success, a dictionary describing the lifeline outcome:
                - For 50/50: keys "lifeline" (str), "remaining_options" (dict of option keys to text), and "message" (str).
                - For SKIP: keys "lifeline" (str), "action" ("skip"), and "message" (str).
                - For UNIVERSITY: keys "lifeline" (str), "votes" (dict with counts for "A","B","C","D"), and "message" (str).
            On failure, a dictionary with an "error" key and a descriptive message (e.g., session not active, lifeline not available, or question not found).
        
        Side effects:
            - Marks the lifeline as used in the session state and persists the updated lifelines to the database.
        """
        state = self.get_session(session_id)
        if not state or state.status != ShowMilhaoStatus.IN_PROGRESS:
            return {"error": "Session not active"}

        if not state.lifelines_available.get(lifeline.value, False):
            return {"error": f"Lifeline {lifeline.value} not available"}

        # Get question
        question = self.supabase.table("questions") \
            .select("options, correct_answer") \
            .eq("id", question_id) \
            .single() \
            .execute()

        if not question.data:
            return {"error": "Question not found"}

        correct = question.data["correct_answer"]
        options = question.data["options"]

        result = {}

        if lifeline == Lifeline.FIFTY_FIFTY:
            # Remove 2 wrong answers
            wrong_options = [k for k in options.keys() if k.upper() != correct.upper()]
            to_remove = random.sample(wrong_options, min(2, len(wrong_options)))
            remaining = {k: v for k, v in options.items() if k.upper() not in [x.upper() for x in to_remove]}
            result = {
                "lifeline": "50/50",
                "remaining_options": remaining,
                "message": f"🎯 50/50: Removidas as opções {', '.join(to_remove)}"
            }

        elif lifeline == Lifeline.SKIP:
            # Skip this question (no penalty, no gain)
            result = {
                "lifeline": "Pular",
                "action": "skip",
                "message": "⏭️ Questão pulada! Sem ganho, sem perda."
            }

        elif lifeline == Lifeline.UNIVERSITY:
            # Simulated university students vote (weighted towards correct)
            votes = {"A": 0, "B": 0, "C": 0, "D": 0}
            for _ in range(100):
                if random.random() < 0.7:  # 70% chance to vote correct
                    votes[correct.upper()] += 1
                else:
                    other = random.choice([k for k in votes.keys() if k != correct.upper()])
                    votes[other] += 1

            result = {
                "lifeline": "Universitários",
                "votes": votes,
                "message": f"🎓 Universitários votaram: A:{votes['A']}% B:{votes['B']}% C:{votes['C']}% D:{votes['D']}%"
            }

        # Mark lifeline as used
        state.lifelines_available[lifeline.value] = False
        state.lifelines_used.append(lifeline.value)

        self.supabase.table("show_milhao_sessions").update({
            "lifelines_available": state.lifelines_available,
            "lifelines_used": state.lifelines_used
        }).eq("id", session_id).execute()

        return result

    def stop_and_take(self, session_id: str) -> Dict:
        """
        End an active Show do Milhão session and award the current pot to the player.
        
        If the session is active, finalizes it as won, awards the current pot as the final prize, and returns a summary of the stopped session. If the session is not active or cannot be found, returns an error.
        
        Returns:
            dict: On success, a dictionary with:
                - "result": "STOPPED"
                - "final_prize": int, the awarded BetCoins
                - "questions_answered": int, number of answered questions in the session
                - "message": str, user-facing confirmation message
            On failure, a dictionary with:
                - "error": str, describing why the operation failed (e.g., "Session not active")
        """
        state = self.get_session(session_id)
        if not state or state.status != ShowMilhaoStatus.IN_PROGRESS:
            return {"error": "Session not active"}

        final_prize = state.current_pot
        self._end_session(session_id, ShowMilhaoStatus.WON, final_prize, state.questions_answered)

        return {
            "result": "STOPPED",
            "final_prize": final_prize,
            "questions_answered": len(state.questions_answered),
            "message": f"🏁 Você parou com {final_prize} BetCoins! Decisão inteligente."
        }

    def _end_session(
        self,
        session_id: str,
        status: ShowMilhaoStatus,
        final_prize: int,
        questions_answered: List[Dict]
    ):
        """
        Finalize a Show do Milhão session by persisting its outcome, awarding any prize, and unlocking the win achievement when applicable.
        
        Updates the session record with the final status, final_prize, questions_answered, and ended_at timestamp. If final_prize is greater than zero, records a SHOW_MILHAO transaction to grant BetCoins to the user. If the session status is WON and exactly 15 questions were answered, unlocks the "show_milhao_win" achievement for the user.
        
        Parameters:
            session_id (str): Identifier of the session to finalize.
            status (ShowMilhaoStatus): Final status of the session.
            final_prize (int): Amount of BetCoins to award as the session prize (0 if none).
            questions_answered (List[Dict]): Recorded answers/details for the session's questions.
        """
        # Update session
        self.supabase.table("show_milhao_sessions").update({
            "status": status.value,
            "final_prize": final_prize,
            "questions_answered": questions_answered,
            "ended_at": datetime.utcnow().isoformat()
        }).eq("id", session_id).execute()

        # Award BetCoins
        if final_prize > 0:
            self.betcoins._record_transaction(
                amount=final_prize,
                transaction_type=TransactionType.SHOW_MILHAO,
                description=f"Show do Milhão: {status.value}",
                reference_id=session_id
            )

        # Check for achievements
        if status == ShowMilhaoStatus.WON and len(questions_answered) == 15:
            self._unlock_achievement("show_milhao_win")

    def _unlock_achievement(self, slug: str):
        """
        Attempt to unlock the achievement identified by `slug` for the current user.
        
        If the achievement exists and is not already unlocked for the user, records the unlock and grants any configured rewards (for example, a betcoin reward).
        Parameters:
            slug (str): Unique achievement identifier (slug) to unlock.
        """
        # Get achievement
        achievement = self.supabase.table("achievements") \
            .select("*") \
            .eq("slug", slug) \
            .single() \
            .execute()

        if not achievement.data:
            return

        # Check if already unlocked
        existing = self.supabase.table("user_achievements") \
            .select("id") \
            .eq("user_id", self.user_id) \
            .eq("achievement_id", achievement.data["id"]) \
            .execute()

        if existing.data:
            return

        # Unlock
        self.supabase.table("user_achievements").insert({
            "user_id": self.user_id,
            "achievement_id": achievement.data["id"]
        }).execute()

        # Award rewards
        if achievement.data.get("betcoin_reward", 0) > 0:
            self.betcoins._record_transaction(
                amount=achievement.data["betcoin_reward"],
                transaction_type=TransactionType.ACHIEVEMENT,
                description=f"Achievement: {achievement.data['name']}"
            )


# =============================================================================
# STREAK ENGINE
# =============================================================================

class StreakEngine:
    """Manages daily streaks"""

    def __init__(self, user_id: str):
        """
        Initialize the instance with the target user's identifier and a Supabase client.
        
        Parameters:
            user_id (str): The unique identifier of the user whose data this instance will operate on.
        """
        self.user_id = user_id
        self.supabase = get_supabase()

    def check_and_update_streak(self) -> Dict[str, Any]:
        """
        Update the user's daily activity streak based on their last active date and return the updated streak summary.
        
        Checks the user's last active timestamp, increments, resets, or preserves the streak as appropriate, updates the user's current and longest streak and last_active_at in storage, and returns a summary of the resulting streak state.
        
        Returns:
            result (dict): A dictionary with keys:
                - current_streak (int): The user's updated current streak (days).
                - longest_streak (int): The user's updated longest streak (days).
                - streak_extended (bool): `True` if the streak increased by one day.
                - streak_broken (bool): `True` if a previous streak was broken and reset.
                - previous_streak (int or None): The previous streak length when `streak_broken` is `True`, otherwise `None`.
                - message (str): A short human-readable message describing the streak outcome.
            If the user is not found, returns:
                {"error": "User not found"}
        """
        user = self.supabase.table("users") \
            .select("current_streak, longest_streak, last_active_at") \
            .eq("id", self.user_id) \
            .single() \
            .execute()

        if not user.data:
            return {"error": "User not found"}

        current_streak = user.data.get("current_streak", 0)
        longest_streak = user.data.get("longest_streak", 0)
        last_active = user.data.get("last_active_at")

        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        new_streak = current_streak
        streak_broken = False
        streak_extended = False

        if last_active:
            last_active_date = datetime.fromisoformat(last_active.replace("Z", "+00:00")).date()

            if last_active_date == today:
                # Already active today, no change
                pass
            elif last_active_date == yesterday:
                # Streak continues!
                new_streak = current_streak + 1
                streak_extended = True
            else:
                # Streak broken
                new_streak = 1
                streak_broken = current_streak > 0
        else:
            # First activity
            new_streak = 1

        # Update longest streak
        new_longest = max(longest_streak, new_streak)

        # Update user
        self.supabase.table("users").update({
            "current_streak": new_streak,
            "longest_streak": new_longest,
            "last_active_at": datetime.utcnow().isoformat()
        }).eq("id", self.user_id).execute()

        result = {
            "current_streak": new_streak,
            "longest_streak": new_longest,
            "streak_extended": streak_extended,
            "streak_broken": streak_broken,
            "previous_streak": current_streak if streak_broken else None
        }

        if streak_extended:
            result["message"] = f"🔥 Streak: {new_streak} dias! Continue assim!"
        elif streak_broken:
            result["message"] = f"💔 Streak de {current_streak} dias quebrado. Começando novo!"
        else:
            result["message"] = f"📅 Streak: {new_streak} dias"

        return result


# =============================================================================
# ACHIEVEMENTS ENGINE
# =============================================================================

class AchievementsEngine:
    """Manages achievements and unlocks"""

    def __init__(self, user_id: str):
        """
        Initialize the engine with the given user context and related services.
        
        Parameters:
            user_id (str): The identifier of the user the engine will operate for. Initializes a Supabase client and a BetCoinsEngine instance bound to this user.
        """
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def check_all_achievements(self) -> List[Dict]:
        """
        Unlocks any achievements the user currently qualifies for.
        
        Checks the user's statistics against all achievement requirements, inserts newly earned achievements into the user's unlocked list, awards configured rewards (e.g., BetCoins, XP), and returns details for each achievement that was unlocked during this check.
        
        Returns:
            List[Dict]: A list of unlocked achievements where each dict contains:
                - name (str): Achievement name.
                - description (str): Achievement description.
                - rarity (str): Achievement rarity.
                - betcoin_reward (int): BetCoins awarded (0 if none).
                - xp_reward (int): XP awarded (0 if none).
        """
        unlocked = []

        # Get user stats
        user = self.supabase.table("users") \
            .select("total_questions_answered, total_correct, current_streak") \
            .eq("id", self.user_id) \
            .single() \
            .execute()

        if not user.data:
            return unlocked

        stats = user.data

        # Get all achievements
        achievements = self.supabase.table("achievements") \
            .select("*") \
            .execute()

        # Get user's unlocked achievements
        user_achievements = self.supabase.table("user_achievements") \
            .select("achievement_id") \
            .eq("user_id", self.user_id) \
            .execute()

        unlocked_ids = [a["achievement_id"] for a in user_achievements.data] if user_achievements.data else []

        for ach in achievements.data or []:
            if ach["id"] in unlocked_ids:
                continue

            should_unlock = False
            req_type = ach["requirement_type"]
            req_value = ach["requirement_value"]

            if req_type == "total_correct" and stats["total_correct"] >= req_value:
                should_unlock = True
            elif req_type == "streak" and stats["current_streak"] >= req_value:
                should_unlock = True

            if should_unlock:
                # Unlock achievement
                self.supabase.table("user_achievements").insert({
                    "user_id": self.user_id,
                    "achievement_id": ach["id"]
                }).execute()

                # Award rewards
                if ach.get("betcoin_reward", 0) > 0:
                    self.betcoins._record_transaction(
                        amount=ach["betcoin_reward"],
                        transaction_type=TransactionType.ACHIEVEMENT,
                        description=f"Achievement: {ach['name']}"
                    )

                unlocked.append({
                    "name": ach["name"],
                    "description": ach["description"],
                    "rarity": ach["rarity"],
                    "betcoin_reward": ach.get("betcoin_reward", 0),
                    "xp_reward": ach.get("xp_reward", 0)
                })

        return unlocked

    def get_user_achievements(self) -> List[Dict]:
        """
        Builds a list of all achievements annotated with the user's unlocked state.
        
        Returns:
            List[Dict]: A list where each item is an achievement dict extended with:
                - "unlocked" (bool): `true` if the user has unlocked the achievement, `false` otherwise.
                - "unlocked_at" (str|None): timestamp when unlocked, or `None` if not unlocked.
        """
        # All achievements
        all_ach = self.supabase.table("achievements") \
            .select("*") \
            .order("rarity") \
            .execute()

        # User's unlocked
        user_ach = self.supabase.table("user_achievements") \
            .select("achievement_id, unlocked_at") \
            .eq("user_id", self.user_id) \
            .execute()

        unlocked_map = {a["achievement_id"]: a["unlocked_at"] for a in user_ach.data} if user_ach.data else {}

        result = []
        for ach in all_ach.data or []:
            result.append({
                **ach,
                "unlocked": ach["id"] in unlocked_map,
                "unlocked_at": unlocked_map.get(ach["id"])
            })

        return result


# =============================================================================
# DAILY CHALLENGE ENGINE
# =============================================================================

class DailyChallengeEngine:
    """Manages daily challenges"""

    def __init__(self, user_id: str):
        """
        Initialize the engine with the given user context and related services.
        
        Parameters:
            user_id (str): The identifier of the user the engine will operate for. Initializes a Supabase client and a BetCoinsEngine instance bound to this user.
        """
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def get_today_challenge(self) -> Optional[Dict]:
        """
        Retrieve today's daily challenge and the user's progress for it.
        
        If a challenge for today does not exist, a new challenge will be generated and returned.
        
        Returns:
            dict: Challenge record merged with:
                - `current_progress` (int): the user's current progress toward the challenge (0 if none).
                - `is_completed` (bool): whether the user has completed the challenge (False if none).
            None: if the challenge could not be retrieved or generated.
        """
        today = datetime.utcnow().date().isoformat()

        result = self.supabase.table("daily_challenges") \
            .select("*") \
            .eq("challenge_date", today) \
            .single() \
            .execute()

        if not result.data:
            # Generate a challenge if none exists
            return self._generate_daily_challenge()

        challenge = result.data

        # Get user's progress
        progress = self.supabase.table("user_daily_challenges") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("challenge_id", challenge["id"]) \
            .single() \
            .execute()

        return {
            **challenge,
            "current_progress": progress.data.get("current_progress", 0) if progress.data else 0,
            "is_completed": progress.data.get("is_completed", False) if progress.data else False
        }

    def _generate_daily_challenge(self) -> Dict:
        """
        Create and persist a new daily challenge record for today.
        
        Selects one challenge from a predefined set, tags it with today's date, inserts it into the `daily_challenges` table, and returns the stored record. If the database insert produces no data, returns the selected challenge dict with the `challenge_date` field set.
        
        Returns:
            dict: The persisted daily challenge record as returned by the database, or the selected challenge dictionary if insertion returned no data.
        """
        today = datetime.utcnow().date().isoformat()

        challenges = [
            {
                "title": "Maratonista",
                "description": "Responda 30 questões hoje",
                "challenge_type": "answer_count",
                "target_value": 30,
                "betcoin_reward": 50,
                "xp_reward": 100
            },
            {
                "title": "Precisão Cirúrgica",
                "description": "Acerte 10 questões seguidas",
                "challenge_type": "correct_streak",
                "target_value": 10,
                "betcoin_reward": 100,
                "xp_reward": 200
            },
            {
                "title": "Speed Run",
                "description": "Responda 20 questões em menos de 30 minutos",
                "challenge_type": "time_challenge",
                "target_value": 20,
                "time_limit_minutes": 30,
                "betcoin_reward": 75,
                "xp_reward": 150
            }
        ]

        selected = random.choice(challenges)
        selected["challenge_date"] = today

        result = self.supabase.table("daily_challenges").insert(selected).execute()

        return result.data[0] if result.data else selected

    def update_progress(self, progress_increment: int = 1) -> Dict:
        """
        Increment the user's progress for today's daily challenge and persist the update.
        
        If no challenge exists for today or the challenge is already completed, a short status dictionary is returned.
        
        Parameters:
            progress_increment (int): Amount to add to the current progress (defaults to 1).
        
        Returns:
            dict: On success, includes:
                - progress (int): Updated current progress after the increment.
                - target (int): Target value required to complete the challenge.
                - is_completed (bool): `true` if the challenge is now completed, `false` otherwise.
                - message (str, optional): Present when the challenge was completed, containing a completion message.
              Early-return forms:
                - {"error": "<message>"} when there is no challenge today.
                - {"message": "<message>"} when the challenge was already completed.
        """
        challenge = self.get_today_challenge()
        if not challenge:
            return {"error": "No challenge today"}

        if challenge.get("is_completed"):
            return {"message": "Challenge already completed!"}

        # Upsert progress
        new_progress = challenge.get("current_progress", 0) + progress_increment
        is_completed = new_progress >= challenge["target_value"]

        self.supabase.table("user_daily_challenges").upsert({
            "user_id": self.user_id,
            "challenge_id": challenge["id"],
            "current_progress": new_progress,
            "is_completed": is_completed,
            "completed_at": datetime.utcnow().isoformat() if is_completed else None
        }).execute()

        result = {
            "progress": new_progress,
            "target": challenge["target_value"],
            "is_completed": is_completed
        }

        if is_completed:
            # Award rewards
            self.betcoins._record_transaction(
                amount=challenge["betcoin_reward"],
                transaction_type=TransactionType.CHALLENGE_WIN,
                description=f"Daily Challenge: {challenge['title']}"
            )
            result["message"] = f"🎉 DESAFIO COMPLETO! +{challenge['betcoin_reward']} BetCoins!"

        return result


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    user_id = "test-user-123"

    # BetCoins
    betcoins = BetCoinsEngine(user_id)
    print(f"Balance: {betcoins.get_balance()}")

    # Show do Milhão
    show = ShowMilhaoEngine(user_id)
    session = show.start_session(initial_stake=50)
    print(f"Session started: {session.session_id}")

    # Get question
    question = show.get_next_question(session.session_id)
    print(f"Question: {question}")