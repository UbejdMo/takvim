from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import City
from app.schemas import CityOut

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", response_model=list[CityOut], summary="List active cities")
async def list_cities(session: AsyncSession = Depends(get_session)) -> list[City]:
    result = await session.execute(
        select(City).where(City.is_active.is_(True)).order_by(City.name_sq)
    )
    return list(result.scalars().all())
