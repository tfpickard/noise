from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from .patterns import PatternResponse


class EmbeddingRequest(BaseModel):
    parameters: dict[str, float] = Field(default_factory=dict)


class SimilarityQuery(BaseModel):
    pattern_id: UUID | None = None
    embedding: list[float] | None = None
    limit: int = Field(default=5, le=50)


class SimilarityResponse(BaseModel):
    results: list[PatternResponse]
