from __future__ import annotations

from pydantic import BaseModel


class QiblaOut(BaseModel):
    """Qibla bearing (degrees clockwise from true north) from a city to the Kaaba."""

    city: str
    latitude: float
    longitude: float
    bearing: float
    distance_km: float
