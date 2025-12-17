"""Gamification routes - Badges, Trust, Avatars"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models.user import User
from models.gamification import Badge, UserBadge, TrustScore, Avatar, Vote
from utils.security import get_current_active_user, get_verified_user

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


class BadgeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    color: str
    earned_at: str | None = None

    class Config:
        from_attributes = True


class TrustScoreResponse(BaseModel):
    karma_points: int
    trust_level: str
    trust_score: float
    upvotes_received: int
    downvotes_received: int
    posts_count: int
    comments_count: int

    class Config:
        from_attributes = True


class AvatarResponse(BaseModel):
    avatar_url: str | None
    avatar_type: str
    background_color: str
    icon: str | None
    show_badges: bool
    show_trust_level: bool

    class Config:
        from_attributes = True


class VoteRequest(BaseModel):
    target_type: str  # 'thread' or 'post'
    target_id: int
    vote_type: int  # 1 or -1


# BADGES
@router.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(db: Session = Depends(get_db)):
    """Get all available badges"""
    badges = db.query(Badge).order_by(Badge.order).all()
    return badges


@router.get("/my-badges", response_model=List[BadgeResponse])
async def get_my_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's earned badges"""
    user_badges = db.query(UserBadge, Badge).join(Badge).filter(
        UserBadge.user_id == current_user.id
    ).all()

    badges_list = []
    for ub, badge in user_badges:
        badge_dict = {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "color": badge.color,
            "earned_at": ub.earned_at.isoformat()
        }
        badges_list.append(badge_dict)

    return badges_list


@router.post("/badges/award/{user_id}/{badge_id}")
async def award_badge(
    user_id: int,
    badge_id: int,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Award a badge to a user (admin/system)"""
    # Check if badge exists
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge não encontrado")

    # Check if user already has this badge
    existing = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Usuário já possui este badge")

    # Award badge
    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
    db.add(user_badge)
    db.commit()

    return {"success": True, "message": f"Badge '{badge.name}' concedido!"}


# TRUST/KARMA
@router.get("/trust/me", response_model=TrustScoreResponse)
async def get_my_trust(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's trust score"""
    trust = db.query(TrustScore).filter(
        TrustScore.user_id == current_user.id
    ).first()

    if not trust:
        # Create initial trust score
        trust = TrustScore(user_id=current_user.id)
        db.add(trust)
        db.commit()
        db.refresh(trust)

    return trust


@router.get("/trust/{user_id}", response_model=TrustScoreResponse)
async def get_user_trust(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a user's trust score"""
    trust = db.query(TrustScore).filter(
        TrustScore.user_id == user_id
    ).first()

    if not trust:
        raise HTTPException(status_code=404, detail="Trust score não encontrado")

    return trust


@router.post("/vote")
async def vote_content(
    vote_data: VoteRequest,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Upvote or downvote content (Reddit-style)"""
    if vote_data.vote_type not in [1, -1]:
        raise HTTPException(status_code=400, detail="vote_type deve ser 1 ou -1")

    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.target_type == vote_data.target_type,
        Vote.target_id == vote_data.target_id
    ).first()

    if existing_vote:
        # Update existing vote
        if existing_vote.vote_type == vote_data.vote_type:
            # Remove vote if clicking same button
            db.delete(existing_vote)
            db.commit()
            return {"action": "removed", "vote_type": None}
        else:
            # Change vote
            existing_vote.vote_type = vote_data.vote_type
            db.commit()
            return {"action": "changed", "vote_type": vote_data.vote_type}
    else:
        # New vote
        vote = Vote(
            user_id=current_user.id,
            target_type=vote_data.target_type,
            target_id=vote_data.target_id,
            vote_type=vote_data.vote_type
        )
        db.add(vote)
        db.commit()

        return {"action": "added", "vote_type": vote_data.vote_type}


# AVATARS
@router.get("/avatar/me", response_model=AvatarResponse)
async def get_my_avatar(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's avatar"""
    avatar = db.query(Avatar).filter(
        Avatar.user_id == current_user.id
    ).first()

    if not avatar:
        # Create default avatar
        avatar = Avatar(user_id=current_user.id)
        db.add(avatar)
        db.commit()
        db.refresh(avatar)

    return avatar


@router.put("/avatar/customize")
async def customize_avatar(
    background_color: Optional[str] = None,
    icon: Optional[str] = None,
    show_badges: Optional[bool] = None,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Customize user's avatar"""
    avatar = db.query(Avatar).filter(
        Avatar.user_id == current_user.id
    ).first()

    if not avatar:
        avatar = Avatar(user_id=current_user.id)
        db.add(avatar)

    if background_color:
        avatar.background_color = background_color
    if icon:
        avatar.icon = icon
    if show_badges is not None:
        avatar.show_badges = show_badges

    db.commit()
    db.refresh(avatar)

    return avatar


@router.post("/avatar/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Upload custom avatar image"""
    # Save avatar file
    import os
    from pathlib import Path

    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user.id}_avatar.{file_ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Update avatar
    avatar = db.query(Avatar).filter(
        Avatar.user_id == current_user.id
    ).first()

    if not avatar:
        avatar = Avatar(user_id=current_user.id)
        db.add(avatar)

    avatar.avatar_url = f"/uploads/avatars/{filename}"
    avatar.avatar_type = "custom"

    db.commit()

    return {"success": True, "avatar_url": avatar.avatar_url}
