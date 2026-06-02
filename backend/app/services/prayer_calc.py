"""Astronomical prayer-time calculation engine.

Pure standard-library implementation (no external deps) of the well-established
sun-position algorithm (cf. PrayTimes.org), specialised for Kosovo / BIK:

* **Standard Asr** — shadow factor 1, as BIK's published takvim uses (the Diyanet-style "BIM
  Kosovo" method; NOT the Hanafi factor-2 variant).
* **Balkan / Diyanet-style twilight angles** — Fajr 18°, Isha 17°.
* **Per-prayer minute offsets (*ihtiyat* / temkin)** — calibration knobs.

IMPORTANT: the app does NOT serve from this engine. Production prayer times are seeded directly
from BIK's official published takvim (see :mod:`app.data.seed` / ``bik_takvim_*.json``), which
reproduces bislame.net to the minute (Immutable rule #1). This engine is kept as a documented
fallback/derivation tool; it approximates BIK to within a few minutes but is not exact.

All angles are in degrees; all times of day are handled as fractional hours and rounded to the
minute at the boundary.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

# --- Degree-based trig helpers ----------------------------------------------------------------


def _sin(d: float) -> float:
    return math.sin(math.radians(d))


def _cos(d: float) -> float:
    return math.cos(math.radians(d))


def _tan(d: float) -> float:
    return math.tan(math.radians(d))


def _arcsin(x: float) -> float:
    return math.degrees(math.asin(x))


def _arccos(x: float) -> float:
    return math.degrees(math.acos(x))


def _arctan2(y: float, x: float) -> float:
    return math.degrees(math.atan2(y, x))


def _arccot(x: float) -> float:
    return math.degrees(math.atan2(1.0, x))


def _fix_angle(a: float) -> float:
    return a - 360.0 * math.floor(a / 360.0)


def _fix_hour(h: float) -> float:
    return h - 24.0 * math.floor(h / 24.0)


# --- Calibration parameters -------------------------------------------------------------------


@dataclass(frozen=True)
class CalcParams:
    """Calibration parameters for the calculation engine.

    ``offsets`` are minute adjustments added after the astronomical computation (positive =
    later). They model BIK's *ihtiyat* (safety margin) and any systematic rounding, and are the
    primary knobs used to reproduce the published takvim exactly.
    """

    fajr_angle: float = 18.0
    isha_angle: float = 17.0
    asr_factor: int = 1  # standard (BIM Kosovo / Diyanet); 2 = Hanafi
    rise_set_angle: float = 0.833  # sun radius + refraction at the horizon
    offsets: dict[str, int] = field(
        default_factory=lambda: {
            "imsak": 0,
            "sunrise": 0,
            "dhuhr": 0,
            "asr": 0,
            "maghrib": 0,
            "isha": 0,
        }
    )


# Parameters approximating the BIK (Bashkësia Islame e Kosovës) takvim, for the fallback engine.
# BIK publishes the standard (factor-1) Asr; the offsets below model its temkin bias.
BIK_PARAMS = CalcParams(
    fajr_angle=18.0,
    isha_angle=17.0,
    asr_factor=1,
    rise_set_angle=0.833,
    offsets={
        "imsak": 0,
        "sunrise": 0,
        "dhuhr": 1,  # BIK biases Dhuhr a minute later (temkin past true zenith)
        "asr": 0,
        "maghrib": 1,  # ihtiyat after astronomical sunset
        "isha": 0,
    },
)

PRAYER_KEYS = ("imsak", "sunrise", "dhuhr", "asr", "maghrib", "isha")


# --- Sun position -----------------------------------------------------------------------------


def _julian(year: int, month: int, day: int) -> float:
    """Julian date at 0h UT for a Gregorian calendar date."""
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100.0)
    b = 2 - a + math.floor(a / 4.0)
    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )


def _sun_position(jd: float) -> tuple[float, float]:
    """Return (declination°, equation-of-time hours) for a Julian date."""
    d = jd - 2451545.0
    g = _fix_angle(357.529 + 0.98560028 * d)  # mean anomaly
    q = _fix_angle(280.459 + 0.98564736 * d)  # mean longitude
    ecl = _fix_angle(q + 1.915 * _sin(g) + 0.020 * _sin(2 * g))  # ecliptic longitude
    obliquity = 23.439 - 0.00000036 * d
    right_ascension = _fix_hour(_arctan2(_cos(obliquity) * _sin(ecl), _cos(ecl)) / 15.0)
    eqt = q / 15.0 - right_ascension  # equation of time, hours
    decl = _arcsin(_sin(obliquity) * _sin(ecl))
    return decl, eqt


# --- Core computation -------------------------------------------------------------------------


def _hours_to_time(hours: float) -> dt.time:
    """Round fractional hours (already in local zone time) to a wall-clock time."""
    total_minutes = int(round(_fix_hour(hours) * 60.0))
    total_minutes %= 24 * 60
    return dt.time(hour=total_minutes // 60, minute=total_minutes % 60)


def _utc_offset_hours(date: dt.date, tz: ZoneInfo) -> float:
    """UTC offset (hours) for the given timezone on the given date, honouring DST."""
    offset = tz.utcoffset(dt.datetime(date.year, date.month, date.day, 12, 0))
    assert offset is not None
    return offset.total_seconds() / 3600.0


def compute_times(
    date: dt.date,
    latitude: float,
    longitude: float,
    *,
    timezone: str = "Europe/Belgrade",
    params: CalcParams = BIK_PARAMS,
) -> dict[str, dt.time]:
    """Compute the six daily times for one location and date.

    Returns a dict keyed by :data:`PRAYER_KEYS`. ``imsak`` is Sabahu/Fajr; ``sunrise`` is
    display-only (Lindja e Diellit). Times are local wall-clock for ``timezone``.
    """
    tz = ZoneInfo(timezone)
    tz_offset = _utc_offset_hours(date, tz)

    # Longitude-corrected Julian base; refine sun position per-time with day fractions.
    j_base = _julian(date.year, date.month, date.day) - longitude / (15.0 * 24.0)

    def mid_day(t: float) -> float:
        _, eqt = _sun_position(j_base + t)
        return _fix_hour(12.0 - eqt)

    def angle_time(angle: float, t: float, *, before_noon: bool) -> float:
        """Time (local hours, pre zone adjustment) at which the sun is ``angle`` below
        the horizon (``angle`` positive = depression below horizon)."""
        decl, _ = _sun_position(j_base + t)
        numerator = -_sin(angle) - _sin(decl) * _sin(latitude)
        denominator = _cos(decl) * _cos(latitude)
        hour_angle = _arccos(max(-1.0, min(1.0, numerator / denominator))) / 15.0
        noon = mid_day(t)
        return noon - hour_angle if before_noon else noon + hour_angle

    def asr_time(t: float) -> float:
        decl, _ = _sun_position(j_base + t)
        # Altitude of the sun when an object's shadow = factor × its length (+ noon shadow).
        altitude = -_arccot(params.asr_factor + _tan(abs(latitude - decl)))
        return angle_time(altitude, t, before_noon=False)

    # Initial day-fraction guesses, then one refinement pass (sub-minute convergence).
    raw = {
        "imsak": angle_time(params.fajr_angle, 5 / 24, before_noon=True),
        "sunrise": angle_time(params.rise_set_angle, 6 / 24, before_noon=True),
        "dhuhr": mid_day(12 / 24),
        "asr": asr_time(13 / 24),
        "maghrib": angle_time(params.rise_set_angle, 18 / 24, before_noon=False),
        "isha": angle_time(params.isha_angle, 18 / 24, before_noon=False),
    }
    raw = {
        "imsak": angle_time(params.fajr_angle, raw["imsak"] / 24, before_noon=True),
        "sunrise": angle_time(params.rise_set_angle, raw["sunrise"] / 24, before_noon=True),
        "dhuhr": mid_day(raw["dhuhr"] / 24),
        "asr": asr_time(raw["asr"] / 24),
        "maghrib": angle_time(params.rise_set_angle, raw["maghrib"] / 24, before_noon=False),
        "isha": angle_time(params.isha_angle, raw["isha"] / 24, before_noon=False),
    }

    zone_adjust = tz_offset - longitude / 15.0
    result: dict[str, dt.time] = {}
    for key in PRAYER_KEYS:
        hours = raw[key] + zone_adjust + params.offsets.get(key, 0) / 60.0
        result[key] = _hours_to_time(hours)
    return result


def day_length(sunrise: dt.time, maghrib: dt.time) -> str:
    """Gjatësia e ditës: maghrib − sunrise as HH:MM (display only)."""
    start = dt.timedelta(hours=sunrise.hour, minutes=sunrise.minute)
    end = dt.timedelta(hours=maghrib.hour, minutes=maghrib.minute)
    minutes = int((end - start).total_seconds() // 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
