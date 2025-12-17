"""Gamification models - Badges, Karma/Trust, Avatars"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from . import Base


class BadgeType(str, enum.Enum):
    NEWCOMER = "newcomer"
    VERIFIED = "verified"
    TRUSTED = "trusted"
    HELPER = "helper"
    EXPERT = "expert"
    VETERAN = "veteran"
    MODERATOR = "moderator"
    CONTRIBUTOR = "contributor"


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    badge_type = Column(String, nullable=False)  # BadgeType enum value
    icon = Column(String)  # Icon URL or emoji
    color = Column(String, default="#3498db")
    points_required = Column(Integer, default=0)
    order = Column(Integer, default=0)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    badge = relationship("Badge", back_populates="user_badges")


class TrustScore(Base):
    """Reddit-style karma/trust system"""
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Trust metrics
    karma_points = Column(Integer, default=0)
    upvotes_received = Column(Integer, default=0)
    downvotes_received = Column(Integer, default=0)
    helpful_answers = Column(Integer, default=0)
    verified_contributions = Column(Integer, default=0)

    # Trust level (calculated field)
    trust_level = Column(String, default="newcomer")  # newcomer, trusted, veteran, expert
    trust_score = Column(Float, default=0.0)  # 0-100 score

    # Activity metrics
    posts_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    days_active = Column(Integer, default=0)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Avatar(Base):
    """Reddit-style avatar system"""
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Avatar customization
    avatar_url = Column(String)  # Custom uploaded avatar
    avatar_type = Column(String, default="default")  # default, custom, generated
    background_color = Column(String, default="#3498db")
    border_color = Column(String)
    icon = Column(String)  # For generated avatars (emoji or icon code)

    # Display preferences
    show_badges = Column(Boolean, default=True)
    show_trust_level = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Vote(Base):
    """Upvote/downvote system for posts and threads"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_type = Column(String, nullable=False)  # 'thread' or 'post'
    target_id = Column(Integer, nullable=False)
    vote_type = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
