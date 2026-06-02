from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.city import Region


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name_sq: str
    name_en: str
    latitude: float
    longitude: float
    region: Region
