from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    host_user_id: UUID | None = None
    title: str = Field(default="Live Session", max_length=120)


class SessionResponse(BaseModel):
    id: UUID
    host_user_id: UUID | None = None
    title: str
    created_at: datetime
    participants: list[str] = Field(default_factory=list)
    is_active: bool = True

    model_config = {"from_attributes": True}
