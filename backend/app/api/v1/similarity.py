from __future__ import annotations

from math import sqrt
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models import Pattern, PatternEmbedding
from app.schemas.patterns import PatternResponse
from app.schemas.similarity import EmbeddingRequest, SimilarityQuery, SimilarityResponse

router = APIRouter()


def _normalize(vec: list[float]) -> list[float]:
    norm = sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


async def _embedding_for_pattern(session: AsyncSession, pattern_id: UUID) -> list[float]:
    embedding = await session.get(PatternEmbedding, pattern_id)
    if embedding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="embedding not found")
    return list(embedding.embedding)


@router.post("/similar", response_model=SimilarityResponse)
async def find_similar(
    payload: SimilarityQuery, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> SimilarityResponse:
    candidate: list[float]
    if payload.pattern_id:
        candidate = await _embedding_for_pattern(session, payload.pattern_id)
    elif payload.embedding:
        candidate = payload.embedding
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="provide pattern_id or embedding")

    candidate_norm = _normalize(candidate)
    embeddings = (await session.scalars(select(PatternEmbedding))).all()
    scored: list[tuple[float, UUID]] = []
    for embedding in embeddings:
        if payload.pattern_id and embedding.pattern_id == str(payload.pattern_id):
            continue
        target = _normalize(list(embedding.embedding))
        score = sum(a * b for a, b in zip(candidate_norm, target))
        scored.append((score, embedding.pattern_id))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top_ids = [pid for _, pid in scored[: payload.limit]]
    patterns = (await session.scalars(select(Pattern).where(Pattern.id.in_(top_ids)))).all()
    return SimilarityResponse(results=[PatternResponse.model_validate(p) for p in patterns])


@router.post("/{pattern_id}/embedding", response_model=dict)
async def create_embedding(
    pattern_id: UUID,
    payload: EmbeddingRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, float]:
    pattern = await session.get(Pattern, pattern_id)
    if pattern is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")
    embedding_values = [float(v) for v in payload.parameters.values()] or [0.0]
    normalized = _normalize(embedding_values)
    upsert = PatternEmbedding(pattern_id=str(pattern_id), embedding=normalized)
    session.merge(upsert)
    await session.commit()
    return {"dimension": len(normalized)}
