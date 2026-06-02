from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.prayer_time import PrayerTime


class Region(str, enum.Enum):
    """Geographic grouping for cities."""

    KOSOVA = "kosova"
    LUGINA = "lugina"  # Preševo Valley


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name_sq: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str] = mapped_column(String(128), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    region: Mapped[Region] = mapped_column(
        Enum(Region, name="region", native_enum=False, length=16),
        default=Region.KOSOVA,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    prayer_times: Mapped[list[PrayerTime]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )
