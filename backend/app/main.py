"""FastAPI application entry point.

Serves official Kosovo (BIK) prayer times, Islamic-calendar events, and Qibla bearings from
PostgreSQL. No authentication, no user accounts (Immutable rule #4).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import cities, events, prayer_times, qibla

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Official Kosovo prayer times (BIK), Islamic events, and Qibla.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(cities.router, prefix=API_PREFIX)
app.include_router(prayer_times.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(qibla.router, prefix=API_PREFIX)


@app.get("/api/health", tags=["meta"], summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok", "timezone": settings.app_timezone}
