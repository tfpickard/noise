from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    pattern_id: UUID
    resolution: str = Field(default="8k", pattern=r"^[0-9]+(k|p)$")
    note: str | None = None


class RenderResponse(BaseModel):
    export_id: UUID = Field(alias="id")
    status: str
    created_at: datetime
    download_url: str | None = Field(default=None, alias="url")
    notes: str | None = None

    model_config = {"populate_by_name": True, "from_attributes": True}
