"""Qibla bearing: great-circle initial heading from a city to the Kaaba."""

from __future__ import annotations

import math

# Kaaba, Mecca.
KAABA_LAT = 21.4225
KAABA_LNG = 39.8262
EARTH_RADIUS_KM = 6371.0088


def qibla_bearing(latitude: float, longitude: float) -> float:
    """Initial great-circle bearing (degrees clockwise from true north) toward the Kaaba."""
    lat1 = math.radians(latitude)
    lat2 = math.radians(KAABA_LAT)
    d_lng = math.radians(KAABA_LNG - longitude)

    y = math.sin(d_lng) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lng)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def great_circle_km(latitude: float, longitude: float) -> float:
    """Great-circle distance (km) from a city to the Kaaba (haversine)."""
    lat1 = math.radians(latitude)
    lat2 = math.radians(KAABA_LAT)
    d_lat = math.radians(KAABA_LAT - latitude)
    d_lng = math.radians(KAABA_LNG - longitude)

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
