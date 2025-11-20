"""Application configuration using Pydantic settings."""

from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/noise_museum"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_echo: bool = False

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    redis_cache_ttl: int = 3600

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_anonymous: str = "100/minute"
    rate_limit_authenticated: str = "1000/minute"
    rate_limit_export: str = "10/minute"

    # Vector Embedding
    embedding_dimensions: int = 128

    # Export Service
    max_export_resolution: int = 8192
    export_timeout_seconds: int = 300

    # Sentry
    sentry_dsn: str | None = None

    @property
    def async_database_url(self) -> str:
        """Get async database URL as string."""
        return str(self.database_url)

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


settings = Settings()
