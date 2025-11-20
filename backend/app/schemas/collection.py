"""Collection schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.pattern import Pattern


class CollectionBase(BaseModel):
    """Base collection schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    is_public: bool = True


class CollectionCreate(CollectionBase):
    """Schema for creating a collection."""

    pass


class CollectionUpdate(BaseModel):
    """Schema for updating a collection."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    is_public: bool | None = None


class CollectionPatternAdd(BaseModel):
    """Schema for adding patterns to a collection."""

    pattern_ids: list[UUID] = Field(..., min_length=1)


class Collection(CollectionBase):
    """Schema for collection response."""

    id: UUID
    user_id: UUID
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    pattern_count: int = 0

    model_config = {"from_attributes": True}


class CollectionWithPatterns(Collection):
    """Schema for collection with patterns."""

    patterns: list[Pattern] = []
