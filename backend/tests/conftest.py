"""Pytest fixtures: in-memory SQLite app with seeded data and a fixed 'today'."""

from __future__ import annotations

import datetime as dt
import os
from collections.abc import AsyncGenerator

# Point the app's module-level engine at SQLite before importing app modules, so tests need no
# Postgres driver (asyncpg). The real Postgres URL is supplied via env in Docker.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_session
from app.main import app
from app.models import City, IslamicEvent, PrayerTime, Region
from app.models.islamic_event import EventType
from app.services import clock
from app.services.prayer_calc import compute_times

# A fixed "today" so /today endpoints are deterministic.
FIXED_TODAY = dt.date(2026, 6, 2)
PRISHTINE = {"slug": "prishtine", "lat": 42.6629, "lng": 21.1655}


@pytest_asyncio.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        city = City(
            slug=PRISHTINE["slug"],
            name_sq="Prishtinë",
            name_en="Pristina",
            latitude=PRISHTINE["lat"],
            longitude=PRISHTINE["lng"],
            region=Region.KOSOVA,
            is_active=True,
        )
        inactive = City(
            slug="ghost",
            name_sq="Ghost",
            name_en="Ghost",
            latitude=0.0,
            longitude=0.0,
            region=Region.KOSOVA,
            is_active=False,
        )
        session.add_all([city, inactive])
        await session.flush()

        for day in (FIXED_TODAY, FIXED_TODAY + dt.timedelta(days=1)):
            t = compute_times(day, PRISHTINE["lat"], PRISHTINE["lng"])
            session.add(PrayerTime(city_id=city.id, date=day, **t))

        session.add(
            IslamicEvent(
                date=FIXED_TODAY,
                hijri_label="17 Dhul-qa'da 1447",
                name_sq="Test Festa",
                name_en="Test Feast",
                type=EventType.HOLIDAY,
            )
        )
        await session.commit()

    async def _override_session() -> AsyncGenerator:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    monkeypatch.setattr(clock, "today", lambda: FIXED_TODAY)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
