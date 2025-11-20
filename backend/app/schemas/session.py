"""Collaboration session schemas for API validation."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Schema for creating a collaboration session."""

    pattern_id: UUID | None = None
    max_participants: int = Field(10, ge=2, le=50)
    expires_in_hours: int = Field(24, ge=1, le=168)


class CollaborationSession(BaseModel):
    """Schema for collaboration session response."""

    id: UUID
    session_code: str
    pattern_id: UUID | None
    owner_id: UUID | None
    current_state: dict[str, Any] | None
    is_active: bool
    max_participants: int
    created_at: datetime
    expires_at: datetime | None
    last_activity_at: datetime

    model_config = {"from_attributes": True}


class SessionMessage(BaseModel):
    """Schema for WebSocket session messages."""

    type: str = Field(..., description="Message type: update, cursor, chat, join, leave")
    user_id: str | None = None
    username: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionJoin(BaseModel):
    """Schema for joining a session."""

    username: str = Field(..., min_length=1, max_length=50)


class SessionUpdate(BaseModel):
    """Schema for session state updates."""

    parameters: dict[str, Any]
    partial: bool = False
