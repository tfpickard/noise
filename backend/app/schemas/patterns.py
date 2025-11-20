from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field


class PatternBase(BaseModel):
    exhibit_type: str = Field(..., max_length=50)
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None
    is_public: bool = True


class PatternCreate(PatternBase):
    user_id: UUID | None = None


class PatternUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    parameters: dict[str, Any] | None = None
    is_public: bool | None = None


class PatternResponse(PatternBase):
    id: UUID
    user_id: UUID | None
    likes_count: int = 0
    views_count: int = 0
    forked_from: UUID | None = None
    created_at: datetime
    updated_at: datetime
    thumbnail_url: str | None = None

    model_config = {
        "from_attributes": True,
    }


class LikeResponse(BaseModel):
    pattern_id: UUID
    likes_count: int


class ForkResponse(BaseModel):
    forked_id: UUID
    parent_id: UUID


class DiscoverResponse(BaseModel):
    patterns: list[PatternResponse]
    next_cursor: Annotated[str | None, Field(description="Cursor for pagination")]
