from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.city import City


class PrayerTime(Base):
    """Six daily prayer times for a city, stored as local Kosovo wall-clock time."""

    __tablename__ = "prayer_times"
    __table_args__ = (UniqueConstraint("city_id", "date", name="uq_prayer_times_city_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[dt.date] = mapped_column(Date, index=True, nullable=False)

    # Imsak == Sabahu (Fajr). Sunrise is display-only (ends Fajr), not a prayer.
    imsak: Mapped[dt.time] = mapped_column(Time, nullable=False)
    sunrise: Mapped[dt.time] = mapped_column(Time, nullable=False)
    dhuhr: Mapped[dt.time] = mapped_column(Time, nullable=False)
    asr: Mapped[dt.time] = mapped_column(Time, nullable=False)
    maghrib: Mapped[dt.time] = mapped_column(Time, nullable=False)
    isha: Mapped[dt.time] = mapped_column(Time, nullable=False)

    city: Mapped[City] = relationship(back_populates="prayer_times")
