"""Analytics schemas for API validation."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event."""

    event_type: str = Field(..., min_length=1, max_length=50)
    pattern_id: UUID | None = None
    session_id: str | None = None
    metadata: dict[str, Any] | None = None


class AnalyticsEvent(AnalyticsEventCreate):
    """Schema for analytics event response."""

    id: UUID
    user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PopularParameters(BaseModel):
    """Schema for popular parameter analysis."""

    exhibit_type: str
    parameter_name: str
    value_distribution: dict[str, int]
    avg_value: float | None = None
    median_value: float | None = None
    sample_count: int


class TrendingPattern(BaseModel):
    """Schema for trending pattern."""

    pattern_id: UUID
    title: str | None
    exhibit_type: str
    likes_count: int
    views_count: int
    forks_count: int
    trending_score: float
    created_at: datetime


class ExhibitUsage(BaseModel):
    """Schema for exhibit usage statistics."""

    exhibit_type: str
    pattern_count: int
    total_views: int
    total_likes: int
    avg_likes_per_pattern: float
    most_recent_created_at: datetime | None
