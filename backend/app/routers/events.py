from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import IslamicEvent
from app.schemas import EventOut
from app.services import clock

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/today", response_model=EventOut | None, summary="Today's event, or null")
async def event_today(session: AsyncSession = Depends(get_session)) -> IslamicEvent | None:
    result = await session.execute(
        select(IslamicEvent).where(IslamicEvent.date == clock.today())
    )
    return result.scalar_one_or_none()


@router.get("", response_model=list[EventOut], summary="All events for a year")
async def events_for_year(
    year: int = Query(..., ge=2000, le=2100),
    session: AsyncSession = Depends(get_session),
) -> list[IslamicEvent]:
    result = await session.execute(
        select(IslamicEvent)
        .where(extract("year", IslamicEvent.date) == year)
        .order_by(IslamicEvent.date)
    )
    return list(result.scalars().all())
