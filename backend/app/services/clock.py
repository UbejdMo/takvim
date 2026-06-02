"""Time helpers anchored to the app timezone (Immutable rule #5: Europe/Belgrade)."""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

from app.core.config import settings


def app_tz() -> ZoneInfo:
    return ZoneInfo(settings.app_timezone)


def now() -> dt.datetime:
    """Current time in the app timezone (Europe/Belgrade)."""
    return dt.datetime.now(app_tz())


def today() -> dt.date:
    """Today's date in the app timezone — the anchor for all 'today' logic."""
    return now().date()
