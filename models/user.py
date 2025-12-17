"""User and authentication models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from . import Base


class UserStatus(str, enum.Enum):
    PENDING_PHONE = "pending_phone"
    PENDING_DOCUMENTS = "pending_documents"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_PHONE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_picture = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    phone_verifications = relationship("PhoneVerification", back_populates="user")
    documents = relationship("DocumentVerification", back_populates="user")
    locations = relationship("UserLocation", back_populates="user")
    forum_threads = relationship("ForumThread", back_populates="author")
    forum_posts = relationship("ForumPost", back_populates="author")
    chat_messages = relationship("ChatMessage", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")


class PhoneVerification(Base):
    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String, nullable=False)
    verification_code = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="phone_verifications")


class DocumentType(str, enum.Enum):
    ID_CARD = "id_card"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    PROOF_OF_ADDRESS = "proof_of_address"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentVerification(Base):
    __tablename__ = "document_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    rejection_reason = Column(Text)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="documents")


class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String)
    accuracy = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="locations")
