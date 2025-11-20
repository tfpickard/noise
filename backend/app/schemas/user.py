"""User schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    display_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema for creating a user."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    """Schema for updating a user."""

    password: str | None = Field(None, min_length=8)


class User(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(User):
    """Schema for user in database (includes hashed password)."""

    hashed_password: str
