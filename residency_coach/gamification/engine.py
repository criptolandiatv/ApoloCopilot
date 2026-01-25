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
        self.user_id = user_id
        self.supabase = get_supabase()

    def get_balance(self) -> int:
        """Get current BetCoin balance"""
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
        """Record a transaction and update balance"""
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
        """Award daily login bonus"""
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
        """Place a bet on a question. Returns (success, bet_amount)"""
        balance = self.get_balance()

        if amount <= 0:
            return True, 0

        if amount > balance:
            amount = balance  # Bet max available

        if amount > balance * 0.5:
            amount = int(balance * 0.5)  # Cap at 50% of balance

        return True, amount

    def resolve_bet(self, amount: int, is_correct: bool, question_id: str) -> BetResult:
        """Resolve a bet after question is answered"""
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
        """Get recent transactions"""
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
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def start_session(
        self,
        initial_stake: int = 0,
        difficulty_mode: str = "classic"
    ) -> ShowMilhaoState:
        """Start a new Show do Milhão session"""

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
        """Get current session state"""
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
        """Get the next question for the session"""
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
        """Process an answer in Show do Milhão"""
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
        """Use a lifeline"""
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
        """Player decides to stop and take current pot"""
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
        """End a session and award prizes"""
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
        """Unlock an achievement for the user"""
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
        self.user_id = user_id
        self.supabase = get_supabase()

    def check_and_update_streak(self) -> Dict[str, Any]:
        """Check and update user's streak on login/activity"""
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
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def check_all_achievements(self) -> List[Dict]:
        """Check all achievements and unlock any that are earned"""
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
        """Get all achievements (unlocked and locked) for display"""
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
        self.user_id = user_id
        self.supabase = get_supabase()
        self.betcoins = BetCoinsEngine(user_id)

    def get_today_challenge(self) -> Optional[Dict]:
        """Get today's challenge"""
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
        """Generate a new daily challenge"""
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
        """Update progress on today's challenge"""
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
