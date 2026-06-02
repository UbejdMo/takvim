from __future__ import annotations

import calendar
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import PrayerTime
from app.routers.deps import get_active_city
from app.schemas import PrayerTimeOut
from app.services import clock

router = APIRouter(prefix="/prayer-times", tags=["prayer-times"])


async def _fetch_one(session: AsyncSession, city_id: int, date: dt.date) -> PrayerTime:
    result = await session.execute(
        select(PrayerTime).where(PrayerTime.city_id == city_id, PrayerTime.date == date)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prayer times seeded for {date.isoformat()}",
        )
    return row


@router.get("/today", response_model=PrayerTimeOut, summary="Today's six times for a city")
async def today(
    city: str = Query(..., description="City slug"),
    session: AsyncSession = Depends(get_session),
) -> PrayerTime:
    city_obj = await get_active_city(session, city)
    return await _fetch_one(session, city_obj.id, clock.today())


@router.get("/month", response_model=list[PrayerTimeOut], summary="A full month for a city")
async def month(
    city: str = Query(..., description="City slug"),
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    session: AsyncSession = Depends(get_session),
) -> list[PrayerTime]:
    city_obj = await get_active_city(session, city)
    last_day = calendar.monthrange(year, month)[1]
    result = await session.execute(
        select(PrayerTime)
        .where(
            PrayerTime.city_id == city_obj.id,
            PrayerTime.date >= dt.date(year, month, 1),
            PrayerTime.date <= dt.date(year, month, last_day),
        )
        .order_by(PrayerTime.date)
    )
    return list(result.scalars().all())


@router.get("/year", response_model=list[PrayerTimeOut], summary="A full year for a city")
async def year(
    city: str = Query(..., description="City slug"),
    year: int = Query(..., ge=2000, le=2100),
    session: AsyncSession = Depends(get_session),
) -> list[PrayerTime]:
    city_obj = await get_active_city(session, city)
    result = await session.execute(
        select(PrayerTime)
        .where(
            PrayerTime.city_id == city_obj.id,
            PrayerTime.date >= dt.date(year, 1, 1),
            PrayerTime.date <= dt.date(year, 12, 31),
        )
        .order_by(PrayerTime.date)
    )
    return list(result.scalars().all())


@router.get("", response_model=PrayerTimeOut, summary="Times for a city on a specific date")
async def on_date(
    city: str = Query(..., description="City slug"),
    date: dt.date = Query(..., description="Date as YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session),
) -> PrayerTime:
    city_obj = await get_active_city(session, city)
    return await _fetch_one(session, city_obj.id, date)
