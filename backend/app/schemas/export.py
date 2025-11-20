from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    pattern_id: UUID
    resolution: str = Field(default="8k", pattern=r"^[0-9]+(k|p)$")


class RenderResponse(BaseModel):
    export_id: UUID
    status: str
    created_at: datetime
    download_url: str | None = None
