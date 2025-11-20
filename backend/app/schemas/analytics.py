from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyticsSlice(BaseModel):
    label: str
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsResponse(BaseModel):
    generated_at: datetime
    slices: list[AnalyticsSlice]
