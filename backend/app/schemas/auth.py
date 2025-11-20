from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    username: str | None = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str | None
    display_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: timedelta
