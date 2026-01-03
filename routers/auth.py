"""Authentication and user management routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

from database import get_db
from models.user import User, UserStatus
from utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: str | None
    status: UserStatus
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        status=UserStatus.PENDING_PHONE,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password"""
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/status")
async def get_verification_status(current_user: User = Depends(get_current_active_user)):
    """Get user verification status"""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "status": current_user.status,
        "is_verified": current_user.is_verified,
        "phone_verified": current_user.status != UserStatus.PENDING_PHONE,
        "documents_verified": current_user.status
        not in [UserStatus.PENDING_PHONE, UserStatus.PENDING_DOCUMENTS],
    }
