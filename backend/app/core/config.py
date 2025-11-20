from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Visual Noise Museum"
    environment: Literal["dev", "staging", "prod"] = "dev"

    backend_cors_origins: list[str] = Field(default_factory=list)
    database_url: str | None = Field(
        default="postgresql+asyncpg://noise:noise@db:5432/noise", alias="DATABASE_URL"
    )
    redis_url: str | None = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    jwt_secret: str = Field("insecure-development-secret", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7

    rate_limit_anonymous_per_minute: int = 100
    rate_limit_authenticated_per_minute: int = 1000

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
