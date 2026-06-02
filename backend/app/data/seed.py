"""Seed the official BIK takvim into PostgreSQL.

Idempotent: re-running upserts cities/events and regenerates prayer times from the committed
official reference data (``bik_takvim_*.json``) plus per-city offsets (``city_offsets.json``).
Run with ``python -m app.data.seed``.

The app serves exclusively from this seeded data — it never calls an external service at
request time (Immutable rule #2). The prayer times ARE BIK's officially published takvim
(the Kosovo reference + each city's minute offset), so they reproduce bislame.net to the
minute (Immutable rule #1). The astronomical engine in :mod:`app.services.prayer_calc` is kept
as a documented fallback/derivation tool and is intentionally NOT used here.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionFactory, engine
from app.data.takvim import PRAYER_FIELDS, TAKVIM_FILES, load_offsets, load_reference, shift
from app.models import City, IslamicEvent, PrayerTime, Region
from app.models.islamic_event import EventType

DATA_DIR = Path(__file__).parent
CITIES_FILE = DATA_DIR / "cities.json"
EVENTS_FILE = DATA_DIR / "events.json"


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


async def _seed_prayer_times(
    session: AsyncSession,
    cities: list[City],
    reference: dict[str, dict[str, str]],
    offsets: dict[str, int],
) -> None:
    dates = sorted(dt.date.fromisoformat(d) for d in reference)
    lo, hi = dates[0], dates[-1]
    total = 0
    for city in cities:
        offset = offsets.get(city.slug, 0)
        # Idempotent: clear the covered range, then regenerate from the official reference.
        await session.execute(
            delete(PrayerTime).where(
                PrayerTime.city_id == city.id,
                PrayerTime.date >= lo,
                PrayerTime.date <= hi,
            )
        )
        rows = [
            PrayerTime(
                city_id=city.id,
                date=dt.date.fromisoformat(date_str),
                **{field: shift(times[field], offset) for field in PRAYER_FIELDS},
            )
            for date_str, times in reference.items()
        ]
        session.add_all(rows)
        await session.commit()
        total += len(rows)
        print(f"  prayer_times: {city.slug} (offset {offset:+d}m) -> {len(rows)} days")
    print(f"  prayer_times: inserted {total} rows total ({lo}..{hi})")


async def seed() -> None:
    reference = load_reference()
    offsets = load_offsets()
    print(
        f"Seeding official BIK takvim: {len(reference)} days "
        f"from {len(TAKVIM_FILES)} file(s) × cities"
    )
    async with SessionFactory() as session:
        cities = await _upsert_cities(session)
        await _upsert_events(session)
        await _seed_prayer_times(session, cities, reference, offsets)
    await engine.dispose()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
