from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EventType(str, enum.Enum):
    DAY = "day"
    NIGHT = "night"
    HOLIDAY = "holiday"


class IslamicEvent(Base):
    __tablename__ = "islamic_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Gregorian date of the event (anchored to Europe/Belgrade).
    date: Mapped[dt.date] = mapped_column(Date, unique=True, index=True, nullable=False)
    hijri_label: Mapped[str] = mapped_column(String(64), nullable=False)
    name_sq: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type", native_enum=False, length=16),
        nullable=False,
    )
    description_sq: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
