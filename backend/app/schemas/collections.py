from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .patterns import PatternResponse


class CollectionCreate(BaseModel):
    user_id: UUID
    title: str = Field(..., max_length=200)
    description: str | None = None
    is_featured: bool = False


class CollectionResponse(CollectionCreate):
    id: UUID
    created_at: datetime
    patterns: list[PatternResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
