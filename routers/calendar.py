"""Google Calendar integration routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
from models.user import User
from models.chat import CalendarEvent
from utils.security import get_verified_user
from services.calendar_service import CalendarService

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])
calendar_service = CalendarService()


class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    location: str | None
    start_time: str
    end_time: str
    is_all_day: bool

    class Config:
        from_attributes = True


@router.get("/auth-url")
async def get_calendar_auth_url(
    current_user: User = Depends(get_verified_user)
):
    """Get Google Calendar authorization URL"""
    auth_url = calendar_service.get_authorization_url()

    return {
        "authorization_url": auth_url,
        "message": "Clique no link para autorizar acesso ao Google Calendar"
    }


@router.get("/callback")
async def calendar_callback(
    code: str = Query(..., description="Authorization code"),
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Handle Google Calendar OAuth callback"""
    try:
        credentials = calendar_service.exchange_code_for_token(code)

        # Sync calendar events
        events = await calendar_service.sync_calendar_events(
            user_id=current_user.id,
            credentials=credentials,
            db=db
        )

        return {
            "success": True,
            "message": "Google Calendar conectado com sucesso!",
            "events_synced": len(events)
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao conectar Google Calendar: {str(e)}"
        )


@router.get("/events", response_model=List[CalendarEventResponse])
async def get_calendar_events(
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Get user's calendar events"""
    events = await calendar_service.get_user_events(
        user_id=current_user.id,
        db=db,
        limit=limit
    )

    return events


@router.post("/sync")
async def sync_calendar(
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Manually sync calendar events"""
    # Note: In production, you would store credentials securely
    # and reuse them here. This is simplified for demonstration.

    return {
        "success": True,
        "message": "Use /auth-url para reconectar e sincronizar eventos"
    }
