"""API endpoint tests against an in-memory SQLite app."""

from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import FIXED_TODAY


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_list_cities_excludes_inactive(client: AsyncClient) -> None:
    resp = await client.get("/api/cities")
    assert resp.status_code == 200
    slugs = {c["slug"] for c in resp.json()}
    assert "prishtine" in slugs
    assert "ghost" not in slugs  # inactive city is hidden


async def test_today_prayer_times(client: AsyncClient) -> None:
    resp = await client.get("/api/prayer-times/today", params={"city": "prishtine"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["date"] == FIXED_TODAY.isoformat()
    for key in ("imsak", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
        assert key in body


async def test_prayer_times_unknown_city_404(client: AsyncClient) -> None:
    resp = await client.get("/api/prayer-times/today", params={"city": "atlantis"})
    assert resp.status_code == 404


async def test_prayer_times_inactive_city_404(client: AsyncClient) -> None:
    resp = await client.get("/api/prayer-times/today", params={"city": "ghost"})
    assert resp.status_code == 404


async def test_prayer_times_on_date(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/prayer-times", params={"city": "prishtine", "date": FIXED_TODAY.isoformat()}
    )
    assert resp.status_code == 200
    assert resp.json()["date"] == FIXED_TODAY.isoformat()


async def test_prayer_times_missing_date_404(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/prayer-times", params={"city": "prishtine", "date": "2030-01-01"}
    )
    assert resp.status_code == 404


async def test_event_today(client: AsyncClient) -> None:
    resp = await client.get("/api/events/today")
    assert resp.status_code == 200
    body = resp.json()
    assert body is not None
    assert body["name_sq"] == "Test Festa"


async def test_events_for_year(client: AsyncClient) -> None:
    resp = await client.get("/api/events", params={"year": 2026})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_qibla(client: AsyncClient) -> None:
    resp = await client.get("/api/qibla", params={"city": "prishtine"})
    assert resp.status_code == 200
    body = resp.json()
    assert 120.0 < body["bearing"] < 160.0
    assert body["city"] == "prishtine"
