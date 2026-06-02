from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict

from app.models.islamic_event import EventType


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: dt.date
    hijri_label: str
    name_sq: str
    name_en: str
    type: EventType
    description_sq: str | None = None
    description_en: str | None = None
