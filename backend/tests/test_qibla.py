"""Tests for the Qibla bearing/distance service."""

from __future__ import annotations

from app.services.qibla import (
    KAABA_LAT,
    KAABA_LNG,
    great_circle_km,
    qibla_bearing,
)

PRISHTINE = (42.6629, 21.1655)


def test_bearing_in_valid_range() -> None:
    bearing = qibla_bearing(*PRISHTINE)
    assert 0.0 <= bearing < 360.0


def test_prishtine_points_south_east() -> None:
    """From Kosovo, Mecca lies roughly south-east; bearing ~130-145 deg."""
    bearing = qibla_bearing(*PRISHTINE)
    assert 120.0 < bearing < 160.0


def test_distance_to_mecca_is_reasonable() -> None:
    # Prishtinë to the Kaaba is ~2930 km great-circle.
    km = great_circle_km(*PRISHTINE)
    assert 2800.0 < km < 3050.0


def test_bearing_from_kaaba_itself_is_defined() -> None:
    # Degenerate but must not raise.
    bearing = qibla_bearing(KAABA_LAT, KAABA_LNG)
    assert 0.0 <= bearing < 360.0
    assert great_circle_km(KAABA_LAT, KAABA_LNG) < 1.0
