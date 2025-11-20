from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.similarity import EmbeddingRequest, SimilarityQuery, SimilarityResponse
from app.schemas.patterns import PatternResponse
from app.services.inmemory_store import store

router = APIRouter()


def _ensure_pattern(pattern_id: UUID) -> None:
    if pattern_id not in store.patterns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")


@router.post("/similar", response_model=SimilarityResponse)
async def find_similar(payload: SimilarityQuery) -> SimilarityResponse:
    results = list(store.patterns.values())[: payload.limit]
    return SimilarityResponse(results=[PatternResponse.model_validate(item) for item in results])


@router.post("/{pattern_id}/embedding", response_model=dict)
async def create_embedding(pattern_id: UUID, payload: EmbeddingRequest) -> dict[str, float]:
    _ensure_pattern(pattern_id)
    embedding = {k: float(v) for k, v in payload.parameters.items()}
    store.patterns[pattern_id]["embedding"] = embedding
    return embedding
