"""Application configuration via pydantic-settings.

All values can be overridden through environment variables (see .env.example).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql+asyncpg://takvimi:change_me_in_prod@localhost:5432/takvimi"

    # --- App ---
    app_name: str = "Takvimi — Kosovo Prayer Times"
    # Every "today / now" computation is anchored to this timezone (Immutable rule #5).
    app_timezone: str = "Europe/Belgrade"
    default_city: str = "prishtine"

    # --- CORS ---
    # NoDecode: keep pydantic-settings from JSON-decoding the env value so the validator below
    # can parse the comma-separated CORS_ORIGINS that docker-compose passes.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
