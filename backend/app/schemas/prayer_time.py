from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class PrayerTimeOut(BaseModel):
    """Six daily times for a city on a given date (local Kosovo wall-clock).

    `imsak` is Sabahu (Fajr); `sunrise` (Lindja e Diellit) is display-only.
    """

    model_config = ConfigDict(from_attributes=True)

    date: dt.date
    imsak: dt.time
    sunrise: dt.time
    dhuhr: dt.time
    asr: dt.time
    maghrib: dt.time
    isha: dt.time
