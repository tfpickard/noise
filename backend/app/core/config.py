from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Visual Noise Museum"
    backend_cors_origins: list[str] = Field(default_factory=list)
    redis_url: str | None = None
    database_url: str | None = None
    jwt_secret: str = "insecure-development-secret"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    return Settings()
