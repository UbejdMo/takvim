"""Shared router dependencies."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City


async def get_active_city(session: AsyncSession, slug: str) -> City:
    """Fetch an active city by slug or raise 404."""
    result = await session.execute(
        select(City).where(City.slug == slug, City.is_active.is_(True))
    )
    city = result.scalar_one_or_none()
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown or inactive city: {slug!r}",
        )
    return city
