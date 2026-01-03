"""Database models for ApoloCopilot"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to ensure they're registered
from .user import User, PhoneVerification, DocumentVerification, UserLocation
from .forum import ForumCategory, ForumThread, ForumPost
from .chat import ChatMessage, CalendarEvent
from .gamification import Badge, UserBadge, TrustScore, Avatar, Vote
from .shifts import Shift, ShiftApplication, ShiftFilter

__all__ = [
    "Base",
    "User",
    "PhoneVerification",
    "DocumentVerification",
    "UserLocation",
    "ForumCategory",
    "ForumThread",
    "ForumPost",
    "ChatMessage",
    "CalendarEvent",
    "Badge",
    "UserBadge",
    "TrustScore",
    "Avatar",
    "Vote",
    "Shift",
    "ShiftApplication",
    "ShiftFilter",
]
