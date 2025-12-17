"""GPS and location routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.user import User
from utils.security import get_verified_user
from services.location_service import LocationService

router = APIRouter(prefix="/api/location", tags=["Location"])
location_service = LocationService()


class LocationData(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None


class GeocodeRequest(BaseModel):
    address: str


@router.post("/save")
async def save_location(
    data: LocationData,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Save user's current location"""
    location = await location_service.save_location(
        user_id=current_user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        db=db,
        accuracy=data.accuracy
    )

    return {
        "success": True,
        "message": "Localização salva",
        "location": {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address
        }
    }


@router.get("/my-location")
async def get_my_location(
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Get user's most recent location"""
    location = await location_service.get_user_location(
        user_id=current_user.id,
        db=db
    )

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma localização encontrada"
        )

    return {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "address": location.address,
        "saved_at": location.created_at.isoformat()
    }


@router.get("/nearby")
async def search_nearby(
    radius_km: float = Query(5.0, description="Raio de busca em km"),
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Search for nearby users/locations"""
    # Get user's current location
    user_location = await location_service.get_user_location(
        user_id=current_user.id,
        db=db
    )

    if not user_location:
        raise HTTPException(
            status_code=400,
            detail="Você precisa salvar sua localização primeiro"
        )

    # Search nearby
    nearby = await location_service.search_nearby(
        latitude=user_location.latitude,
        longitude=user_location.longitude,
        radius_km=radius_km,
        db=db
    )

    return {
        "center": {
            "latitude": user_location.latitude,
            "longitude": user_location.longitude
        },
        "radius_km": radius_km,
        "results": nearby,
        "count": len(nearby)
    }


@router.post("/geocode")
async def geocode_address(
    data: GeocodeRequest,
    current_user: User = Depends(get_verified_user)
):
    """Convert address to coordinates"""
    result = await location_service.geocode_address(data.address)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Endereço não encontrado"
        )

    return result


@router.get("/request-permission")
async def request_gps_permission():
    """Information about GPS permission requirements"""
    return {
        "message": "GPS permission required",
        "reason": "Para usar recursos de localização e mapa, precisamos de permissão para acessar sua localização.",
        "permissions": [
            "ACCESS_FINE_LOCATION",
            "ACCESS_COARSE_LOCATION"
        ],
        "usage": [
            "Mostrar sua localização no mapa",
            "Buscar locais próximos",
            "Navegação estilo Uber"
        ]
    }
