"""Medical shifts/plantões routes"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.shifts import Shift, ShiftApplication, ShiftFilter, ShiftType, ShiftSource
from utils.security import get_verified_user

router = APIRouter(prefix="/api/shifts", tags=["Medical Shifts"])


class ShiftResponse(BaseModel):
    id: int
    title: str
    description: str | None
    shift_type: str
    source: str
    hospital_name: str | None
    city: str | None
    state: str | None
    shift_date: str | None
    shift_duration_hours: float | None
    total_pay: float | None
    is_active: bool
    applications_count: int

    class Config:
        from_attributes = True


class ShiftCreate(BaseModel):
    title: str
    description: Optional[str] = None
    shift_type: str
    source: str
    source_url: Optional[str] = None
    hospital_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    shift_date: Optional[datetime] = None
    shift_duration_hours: Optional[float] = None
    pay_rate: Optional[float] = None
    total_pay: Optional[float] = None
    specialty_required: Optional[str] = None


class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = None


@router.get("/search", response_model=List[ShiftResponse])
async def search_shifts(
    city: Optional[str] = None,
    shift_type: Optional[str] = None,
    min_pay: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Search for available medical shifts"""
    query = db.query(Shift).filter(Shift.is_active == True, Shift.is_filled == False)

    if city:
        query = query.filter(Shift.city.ilike(f"%{city}%"))

    if shift_type:
        query = query.filter(Shift.shift_type == shift_type)

    if min_pay:
        query = query.filter(Shift.total_pay >= min_pay)

    # TODO: Implement distance filter using user's location

    shifts = query.order_by(Shift.shift_date).limit(limit).all()

    return shifts


@router.post("/create", response_model=ShiftResponse)
async def create_shift(
    shift_data: ShiftCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Create a new shift opportunity"""
    shift = Shift(**shift_data.dict())

    db.add(shift)
    db.commit()
    db.refresh(shift)

    return shift


@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(shift_id: int, db: Session = Depends(get_db)):
    """Get shift details"""
    shift = db.query(Shift).filter(Shift.id == shift_id).first()

    if not shift:
        raise HTTPException(status_code=404, detail="Plantão não encontrado")

    return shift


@router.post("/{shift_id}/apply")
async def apply_to_shift(
    shift_id: int,
    application_data: ApplicationCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Apply to a shift"""
    # Check if shift exists
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Plantão não encontrado")

    if shift.is_filled:
        raise HTTPException(status_code=400, detail="Plantão já preenchido")

    # Check if already applied
    existing = (
        db.query(ShiftApplication)
        .filter(ShiftApplication.shift_id == shift_id, ShiftApplication.user_id == current_user.id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Você já se candidatou a este plantão")

    # Create application
    application = ShiftApplication(
        shift_id=shift_id, user_id=current_user.id, cover_letter=application_data.cover_letter
    )

    db.add(application)

    # Increment applications count
    shift.applications_count += 1

    db.commit()

    return {"success": True, "message": "Candidatura enviada com sucesso!"}


@router.get("/my/applications")
async def get_my_applications(
    current_user: User = Depends(get_verified_user), db: Session = Depends(get_db)
):
    """Get user's shift applications"""
    applications = (
        db.query(ShiftApplication, Shift)
        .join(Shift)
        .filter(ShiftApplication.user_id == current_user.id)
        .order_by(ShiftApplication.applied_at.desc())
        .all()
    )

    results = []
    for app, shift in applications:
        results.append(
            {
                "application_id": app.id,
                "status": app.status,
                "applied_at": app.applied_at.isoformat(),
                "shift": {
                    "id": shift.id,
                    "title": shift.title,
                    "hospital_name": shift.hospital_name,
                    "shift_date": shift.shift_date.isoformat() if shift.shift_date else None,
                    "total_pay": shift.total_pay,
                },
            }
        )

    return results


@router.post("/scrape/google-jobs", include_in_schema=False)
async def scrape_google_jobs(
    background_tasks: BackgroundTasks, query: str = "plantão médico", location: str = "Brasil"
):
    """Scrape medical shifts from Google Jobs (background task)"""
    # This would be a background task that scrapes Google Jobs
    # For now, return a placeholder response

    return {
        "success": True,
        "message": "Busca de plantões iniciada em background",
        "query": query,
        "location": location,
    }


@router.get("/filters/my")
async def get_my_filters(
    current_user: User = Depends(get_verified_user), db: Session = Depends(get_db)
):
    """Get user's saved shift filters"""
    filters = db.query(ShiftFilter).filter(ShiftFilter.user_id == current_user.id).first()

    if not filters:
        return {"message": "Nenhum filtro configurado"}

    return filters


@router.post("/filters/save")
async def save_filters(
    shift_types: Optional[List[str]] = None,
    cities: Optional[List[str]] = None,
    min_pay: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Save shift search filters"""
    import json

    filters = db.query(ShiftFilter).filter(ShiftFilter.user_id == current_user.id).first()

    if not filters:
        filters = ShiftFilter(user_id=current_user.id)
        db.add(filters)

    if shift_types:
        filters.shift_types = json.dumps(shift_types)
    if cities:
        filters.cities = json.dumps(cities)
    if min_pay:
        filters.min_pay = min_pay
    if max_distance_km:
        filters.max_distance_km = max_distance_km

    db.commit()

    return {"success": True, "message": "Filtros salvos com sucesso"}


@router.get("/types")
async def get_shift_types():
    """Get available shift types"""
    return {
        "shift_types": [
            {"value": "emergency", "label": "Emergência"},
            {"value": "icu", "label": "UTI"},
            {"value": "surgery", "label": "Cirurgia"},
            {"value": "general", "label": "Geral"},
            {"value": "pediatrics", "label": "Pediatria"},
            {"value": "obstetrics", "label": "Obstetrícia"},
            {"value": "other", "label": "Outro"},
        ]
    }
