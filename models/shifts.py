"""Medical shifts/plantões models"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from . import Base


class ShiftType(str, enum.Enum):
    EMERGENCY = "emergency"  # Plantão de emergência
    ICU = "icu"  # UTI
    SURGERY = "surgery"  # Cirurgia
    GENERAL = "general"  # Geral
    PEDIATRICS = "pediatrics"  # Pediatria
    OBSTETRICS = "obstetrics"  # Obstetrícia
    OTHER = "other"


class ShiftSource(str, enum.Enum):
    GOOGLE_JOBS = "google_jobs"
    MANUAL = "manual"
    PLANTAOMEDICO = "plantaomedico"
    INFOJOBS = "infojobs"
    OTHER_APP = "other_app"


class Shift(Base):
    """Medical shifts/plantões opportunities"""

    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    shift_type = Column(String, nullable=False)  # ShiftType enum
    source = Column(String, nullable=False)  # ShiftSource enum
    source_url = Column(String)

    # Location
    hospital_name = Column(String)
    city = Column(String)
    state = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    # Shift details
    shift_date = Column(DateTime(timezone=True))
    shift_duration_hours = Column(Float)
    pay_rate = Column(Float)  # Hourly rate
    total_pay = Column(Float)

    # Requirements
    specialty_required = Column(String)
    experience_required = Column(String)

    # Status
    is_active = Column(Boolean, default=True)
    is_filled = Column(Boolean, default=False)
    applications_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    applications = relationship("ShiftApplication", back_populates="shift")


class ShiftApplication(Base):
    """User applications to shifts"""

    __tablename__ = "shift_applications"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="pending")  # pending, accepted, rejected, withdrawn
    cover_letter = Column(Text)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    shift = relationship("Shift", back_populates="applications")


class ShiftFilter(Base):
    """User's saved shift filters/preferences"""

    __tablename__ = "shift_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Filter criteria
    shift_types = Column(Text)  # JSON array of shift types
    cities = Column(Text)  # JSON array of cities
    min_pay = Column(Float)
    max_distance_km = Column(Float)

    # Notifications
    notify_new_shifts = Column(Boolean, default=True)
    notify_via_whatsapp = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
