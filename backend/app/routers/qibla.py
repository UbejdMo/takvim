from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.routers.deps import get_active_city
from app.schemas import QiblaOut
from app.services.qibla import great_circle_km, qibla_bearing

router = APIRouter(prefix="/qibla", tags=["qibla"])


@router.get("", response_model=QiblaOut, summary="Qibla bearing from a city")
async def qibla(
    city: str = Query(..., description="City slug"),
    session: AsyncSession = Depends(get_session),
) -> QiblaOut:
    city_obj = await get_active_city(session, city)
    return QiblaOut(
        city=city_obj.slug,
        latitude=city_obj.latitude,
        longitude=city_obj.longitude,
        bearing=round(qibla_bearing(city_obj.latitude, city_obj.longitude), 2),
        distance_km=round(great_circle_km(city_obj.latitude, city_obj.longitude), 1),
    )
