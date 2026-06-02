"""Seed the official takvim into PostgreSQL.

Idempotent: re-running upserts cities/events and regenerates prayer times for the configured
years. Run with ``python -m app.data.seed``.

The app serves exclusively from this seeded data — it never calls an external service at
request time (Immutable rule #2). Prayer times come from the calibrated calculation engine
(:mod:`app.services.prayer_calc`); calibrate and validate against BIK before treating the
output as official (Immutable rule #1).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import SessionFactory, engine
from app.models import City, IslamicEvent, PrayerTime, Region
from app.models.islamic_event import EventType
from app.services import clock
from app.services.prayer_calc import compute_times

DATA_DIR = Path(__file__).parent
CITIES_FILE = DATA_DIR / "cities.json"
EVENTS_FILE = DATA_DIR / "events.json"


def _seed_years() -> list[int]:
    """Years to generate prayer times for (env SEED_YEARS, else this year + next)."""
    raw = os.getenv("SEED_YEARS")
    if raw:
        return [int(y.strip()) for y in raw.split(",") if y.strip()]
    this_year = clock.today().year
    return [this_year, this_year + 1]


async def _upsert_cities(session: AsyncSession) -> list[City]:
    records = json.loads(CITIES_FILE.read_text(encoding="utf-8"))
    cities: list[City] = []
    for rec in records:
        existing = (
            await session.execute(select(City).where(City.slug == rec["slug"]))
        ).scalar_one_or_none()
        if existing is None:
            existing = City(slug=rec["slug"])
            session.add(existing)
        existing.name_sq = rec["name_sq"]
        existing.name_en = rec["name_en"]
        existing.latitude = rec["latitude"]
        existing.longitude = rec["longitude"]
        existing.region = Region(rec["region"])
        existing.is_active = rec.get("is_active", True)
        cities.append(existing)
    await session.commit()
    print(f"  cities: upserted {len(cities)}")
    return cities


async def _upsert_events(session: AsyncSession) -> None:
    records = json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
    for rec in records:
        date = dt.date.fromisoformat(rec["date"])
        existing = (
            await session.execute(select(IslamicEvent).where(IslamicEvent.date == date))
        ).scalar_one_or_none()
        if existing is None:
            existing = IslamicEvent(date=date)
            session.add(existing)
        existing.hijri_label = rec["hijri_label"]
        existing.name_sq = rec["name_sq"]
        existing.name_en = rec["name_en"]
        existing.type = EventType(rec["type"])
        existing.description_sq = rec.get("description_sq")
        existing.description_en = rec.get("description_en")
    await session.commit()
    print(f"  events: upserted {len(records)}")


async def _seed_prayer_times(session: AsyncSession, cities: list[City], years: list[int]) -> None:
    total = 0
    for city in cities:
        for year in years:
            # Idempotent: clear the year then regenerate.
            await session.execute(
                delete(PrayerTime).where(
                    PrayerTime.city_id == city.id,
                    PrayerTime.date >= dt.date(year, 1, 1),
                    PrayerTime.date <= dt.date(year, 12, 31),
                )
            )
            rows: list[PrayerTime] = []
            day = dt.date(year, 1, 1)
            end = dt.date(year, 12, 31)
            while day <= end:
                t = compute_times(
                    day,
                    city.latitude,
                    city.longitude,
                    timezone=settings.app_timezone,
                )
                rows.append(
                    PrayerTime(
                        city_id=city.id,
                        date=day,
                        imsak=t["imsak"],
                        sunrise=t["sunrise"],
                        dhuhr=t["dhuhr"],
                        asr=t["asr"],
                        maghrib=t["maghrib"],
                        isha=t["isha"],
                    )
                )
                day += dt.timedelta(days=1)
            session.add_all(rows)
            await session.commit()
            total += len(rows)
        print(f"  prayer_times: {city.slug} -> {len(years)} year(s)")
    print(f"  prayer_times: inserted {total} rows total")


async def seed() -> None:
    years = _seed_years()
    print(f"Seeding takvim for years {years} (timezone {settings.app_timezone})")
    async with SessionFactory() as session:
        cities = await _upsert_cities(session)
        await _upsert_events(session)
        await _seed_prayer_times(session, cities, years)
    await engine.dispose()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
