"""Tests for the astronomical prayer-time engine."""

from __future__ import annotations

import datetime as dt

import pytest

from app.services.prayer_calc import (
    PRAYER_KEYS,
    BIK_PARAMS,
    CalcParams,
    compute_times,
    day_length,
)

PRISHTINE = (42.6629, 21.1655)

SAMPLE_DATES = [
    dt.date(2026, 1, 15),  # winter (CET, +1)
    dt.date(2026, 3, 21),  # equinox
    dt.date(2026, 6, 21),  # summer solstice (CEST, +2)
    dt.date(2026, 9, 23),  # equinox
    dt.date(2026, 12, 21),  # winter solstice
]


@pytest.mark.parametrize("date", SAMPLE_DATES)
def test_times_are_strictly_ordered(date: dt.date) -> None:
    t = compute_times(date, *PRISHTINE)
    ordered = [t[k] for k in PRAYER_KEYS]
    assert ordered == sorted(ordered), f"{date}: times out of order {ordered}"


@pytest.mark.parametrize("date", SAMPLE_DATES)
def test_dhuhr_near_local_noon(date: dt.date) -> None:
    t = compute_times(date, *PRISHTINE)
    assert dt.time(11, 30) <= t["dhuhr"] <= dt.time(13, 30)


def test_asr_factor_two_is_later_than_factor_one() -> None:
    """Engine supports both Asr conventions: factor 2 (Hanafi) falls later than factor 1."""
    date = dt.date(2026, 6, 21)
    hanafi = CalcParams(asr_factor=2, offsets=BIK_PARAMS.offsets)
    standard = CalcParams(asr_factor=1, offsets=BIK_PARAMS.offsets)
    assert compute_times(date, *PRISHTINE, params=hanafi)["asr"] > (
        compute_times(date, *PRISHTINE, params=standard)["asr"]
    )


def test_bik_params_use_standard_asr() -> None:
    """BIK's published takvim uses the standard (factor-1) Asr, so that is the BIK default."""
    assert BIK_PARAMS.asr_factor == 1


def test_dst_shifts_wall_clock_between_winter_and_summer() -> None:
    """Belgrade is +1 in January and +2 in June; sunrise wall-clock must differ accordingly."""
    winter = compute_times(dt.date(2026, 1, 15), *PRISHTINE)
    summer = compute_times(dt.date(2026, 6, 21), *PRISHTINE)
    # Summer sunrise is much earlier on the clock than winter sunrise.
    assert summer["sunrise"] < winter["sunrise"]


def test_offsets_apply_in_minutes() -> None:
    base = CalcParams(offsets={k: 0 for k in PRAYER_KEYS})
    bumped = CalcParams(offsets={**{k: 0 for k in PRAYER_KEYS}, "dhuhr": 5})
    a = compute_times(dt.date(2026, 6, 2), *PRISHTINE, params=base)
    b = compute_times(dt.date(2026, 6, 2), *PRISHTINE, params=bumped)
    diff = (
        dt.datetime.combine(dt.date.min, b["dhuhr"])
        - dt.datetime.combine(dt.date.min, a["dhuhr"])
    )
    assert diff == dt.timedelta(minutes=5)


def test_day_length_format() -> None:
    t = compute_times(dt.date(2026, 6, 21), *PRISHTINE)
    length = day_length(t["sunrise"], t["maghrib"])
    assert len(length) == 5 and length[2] == ":"
    hours = int(length[:2])
    assert 14 <= hours <= 16  # long summer day in Kosovo
