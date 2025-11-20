"""Pattern schemas for API validation."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PatternBase(BaseModel):
    """Base pattern schema."""

    exhibit_type: str = Field(..., min_length=1, max_length=50)
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    parameters: dict[str, Any] = Field(..., description="Noise generation parameters")
    seed: int | None = None
    is_public: bool = True


class PatternCreate(PatternBase):
    """Schema for creating a pattern."""

    pass


class PatternUpdate(BaseModel):
    """Schema for updating a pattern."""

    title: str | None = Field(None, max_length=200)
    description: str | None = None
    parameters: dict[str, Any] | None = None
    is_public: bool | None = None


class Pattern(PatternBase):
    """Schema for pattern response."""

    id: UUID
    user_id: UUID | None
    thumbnail_url: str | None
    likes_count: int
    views_count: int
    forks_count: int
    forked_from_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatternList(BaseModel):
    """Schema for paginated pattern list."""

    items: list[Pattern]
    total: int
    page: int
    page_size: int
    has_more: bool


class PatternEmbedding(BaseModel):
    """Schema for pattern embedding."""

    pattern_id: UUID
    embedding: list[float] = Field(..., min_length=128, max_length=128)
    created_at: datetime

    model_config = {"from_attributes": True}


class SimilaritySearch(BaseModel):
    """Schema for similarity search request."""

    pattern_id: UUID | None = None
    embedding: list[float] | None = Field(None, min_length=128, max_length=128)
    limit: int = Field(10, ge=1, le=100)
    threshold: float = Field(0.7, ge=0.0, le=1.0)


class PatternFork(BaseModel):
    """Schema for forking a pattern."""

    title: str | None = Field(None, max_length=200)
    description: str | None = None
    parameters: dict[str, Any] | None = None
