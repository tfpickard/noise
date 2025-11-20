from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.patterns import (
    DiscoverResponse,
    ForkResponse,
    LikeResponse,
    PatternCreate,
    PatternResponse,
    PatternUpdate,
)
from app.services.inmemory_store import store

router = APIRouter()


def _get_pattern(pattern_id: UUID) -> dict[str, Any]:
    pattern = store.patterns.get(pattern_id)
    if pattern is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")
    return pattern


@router.post("", response_model=PatternResponse)
async def create_pattern(payload: PatternCreate) -> PatternResponse:
    record = store.create_pattern(payload.model_dump())
    return PatternResponse.model_validate(record)


@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(pattern_id: UUID) -> PatternResponse:
    return PatternResponse.model_validate(_get_pattern(pattern_id))


@router.get("/user/{user_id}", response_model=list[PatternResponse])
async def get_user_patterns(user_id: UUID) -> list[PatternResponse]:
    records = [p for p in store.patterns.values() if p.get("user_id") == user_id]
    return [PatternResponse.model_validate(item) for item in records]


@router.put("/{pattern_id}", response_model=PatternResponse)
async def update_pattern(pattern_id: UUID, payload: PatternUpdate) -> PatternResponse:
    _get_pattern(pattern_id)
    record = store.update_pattern(pattern_id, payload.model_dump())
    return PatternResponse.model_validate(record)


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern(pattern_id: UUID) -> None:
    _get_pattern(pattern_id)
    store.patterns.pop(pattern_id)


@router.get("/discover", response_model=DiscoverResponse)
async def discover(cursor: str | None = None, limit: int = 10) -> DiscoverResponse:
    patterns = list(store.patterns.values())[:limit]
    next_cursor = cursor if len(patterns) == limit else None
    return DiscoverResponse(patterns=[PatternResponse.model_validate(p) for p in patterns], next_cursor=next_cursor)


@router.post("/{pattern_id}/like", response_model=LikeResponse)
async def like_pattern(pattern_id: UUID, user_id: UUID | None = None) -> LikeResponse:
    _get_pattern(pattern_id)
    count = store.like_pattern(pattern_id, user_id)
    return LikeResponse(pattern_id=pattern_id, likes_count=count)


@router.delete("/{pattern_id}/like", response_model=LikeResponse)
async def unlike_pattern(pattern_id: UUID, user_id: UUID | None = None) -> LikeResponse:
    _get_pattern(pattern_id)
    count = store.unlike_pattern(pattern_id, user_id)
    return LikeResponse(pattern_id=pattern_id, likes_count=count)


@router.post("/{pattern_id}/fork", response_model=ForkResponse)
async def fork_pattern(pattern_id: UUID, payload: PatternCreate) -> ForkResponse:
    _get_pattern(pattern_id)
    forked = store.fork_pattern(pattern_id, payload.model_dump())
    return ForkResponse(forked_id=forked["id"], parent_id=pattern_id)


@router.get("/{pattern_id}/forks", response_model=list[PatternResponse])
async def get_forks(pattern_id: UUID) -> list[PatternResponse]:
    forks = [p for p in store.patterns.values() if p.get("forked_from") == pattern_id]
    return [PatternResponse.model_validate(item) for item in forks]
