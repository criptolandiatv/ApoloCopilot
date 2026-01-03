"""GPS and location service"""

from typing import Optional, List
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from models.user import UserLocation


class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="apolocopilot")

    async def save_location(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        db: Session,
        accuracy: Optional[float] = None,
    ) -> UserLocation:
        """Save user location"""
        # Reverse geocode to get address
        address = await self._get_address(latitude, longitude)

        location = UserLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            address=address,
            accuracy=accuracy,
        )

        db.add(location)
        db.commit()
        db.refresh(location)

        return location

    async def _get_address(self, latitude: float, longitude: float) -> str:
        """Get address from coordinates"""
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                return location.address
        except Exception as e:
            print(f"Geocoding error: {e}")

        return f"{latitude}, {longitude}"

    async def get_user_location(self, user_id: int, db: Session) -> Optional[UserLocation]:
        """Get user's most recent location"""
        return (
            db.query(UserLocation)
            .filter(UserLocation.user_id == user_id)
            .order_by(UserLocation.created_at.desc())
            .first()
        )

    async def search_nearby(
        self, latitude: float, longitude: float, radius_km: float, db: Session
    ) -> List[dict]:
        """Search for users/locations nearby"""
        # Get all recent locations
        all_locations = db.query(UserLocation).order_by(UserLocation.created_at.desc()).all()

        nearby = []
        user_point = (latitude, longitude)

        for location in all_locations:
            location_point = (location.latitude, location.longitude)
            distance = geodesic(user_point, location_point).kilometers

            if distance <= radius_km:
                nearby.append(
                    {
                        "user_id": location.user_id,
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "address": location.address,
                        "distance_km": round(distance, 2),
                    }
                )

        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])

        return nearby

    async def geocode_address(self, address: str) -> Optional[dict]:
        """Convert address to coordinates"""
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address,
                }
        except Exception as e:
            print(f"Geocoding error: {e}")

        return None
