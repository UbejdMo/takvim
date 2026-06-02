"""API routers (all mounted under /api)."""

from app.routers import cities, events, prayer_times, qibla

__all__ = ["cities", "events", "prayer_times", "qibla"]
