from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, get_redis, rate_limit_dependency
from app.models import Pattern, PatternLike, User
from app.schemas.patterns import (
    DiscoverResponse,
    ForkResponse,
    LikeResponse,
    PatternCreate,
    PatternResponse,
    PatternUpdate,
)

router = APIRouter()


async def _get_pattern(session: AsyncSession, pattern_id: UUID) -> Pattern:
    pattern = await session.get(Pattern, pattern_id)
    if pattern is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")
    return pattern


@router.post("", response_model=PatternResponse, dependencies=[rate_limit_dependency("patterns:create", True)])
async def create_pattern(
    payload: PatternCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User | None, Depends(get_current_user)] = None,
) -> PatternResponse:
    record = Pattern(
        user_id=payload.user_id or (user.id if user else None),
        exhibit_type=payload.exhibit_type,
        title=payload.title,
        description=payload.description,
        parameters=payload.parameters,
        seed=payload.seed,
        is_public=payload.is_public,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return PatternResponse.model_validate(record)


@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(
    pattern_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> PatternResponse:
    record = await _get_pattern(session, pattern_id)
    return PatternResponse.model_validate(record)


@router.get("/user/{user_id}", response_model=list[PatternResponse])
async def get_user_patterns(
    user_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> list[PatternResponse]:
    stmt = select(Pattern).where(Pattern.user_id == user_id).order_by(Pattern.created_at.desc())
    records = (await session.scalars(stmt)).all()
    return [PatternResponse.model_validate(item) for item in records]


@router.put("/{pattern_id}", response_model=PatternResponse, dependencies=[rate_limit_dependency("patterns:update", True)])
async def update_pattern(
    pattern_id: UUID,
    payload: PatternUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PatternResponse:
    record = await _get_pattern(session, pattern_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await session.commit()
    await session.refresh(record)
    return PatternResponse.model_validate(record)


@router.delete(
    "/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[rate_limit_dependency("patterns:delete", True)]
)
async def delete_pattern(pattern_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
    record = await _get_pattern(session, pattern_id)
    await session.delete(record)
    await session.commit()


@router.get("/discover", response_model=DiscoverResponse)
async def discover(
    cursor: str | None = None,
    limit: int = 10,
    session: Annotated[AsyncSession, Depends(get_db_session)] = Depends(),
) -> DiscoverResponse:
    stmt = select(Pattern).order_by(Pattern.created_at.desc()).limit(limit)
    records = (await session.scalars(stmt)).all()
    next_cursor = cursor if len(records) == limit else None
    return DiscoverResponse(patterns=[PatternResponse.model_validate(p) for p in records], next_cursor=next_cursor)


@router.get("/trending", response_model=list[PatternResponse])
async def trending(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis = Depends(get_redis),
) -> list[PatternResponse]:
    cache_key = "patterns:trending"
    cached = None
    if redis:
        cached = await redis.get(cache_key)
    if cached:
        # cache holds pattern IDs comma-separated
        ids = [UUID(item) for item in cached.split(",") if item]
        records = [await session.get(Pattern, pid) for pid in ids]
        return [PatternResponse.model_validate(r) for r in records if r]

    stmt = select(Pattern).order_by(Pattern.likes_count.desc(), Pattern.created_at.desc()).limit(10)
    records = (await session.scalars(stmt)).all()
    if redis:
        await redis.set(cache_key, ",".join(str(r.id) for r in records), ex=30)
    return [PatternResponse.model_validate(r) for r in records]


@router.post("/{pattern_id}/like", response_model=LikeResponse, dependencies=[rate_limit_dependency("patterns:like")])
async def like_pattern(
    pattern_id: UUID,
    user: Annotated[User | None, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db_session)] = Depends(),
) -> LikeResponse:
    record = await _get_pattern(session, pattern_id)
    liker_id = user.id if user else None
    if liker_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user required")
    existing = await session.get(PatternLike, {"pattern_id": pattern_id, "user_id": liker_id})
    if existing:
        return LikeResponse(pattern_id=pattern_id, likes_count=record.likes_count)
    like = PatternLike(pattern_id=pattern_id, user_id=liker_id)
    session.add(like)
    record.likes_count += 1
    await session.commit()
    await session.refresh(record)
    return LikeResponse(pattern_id=pattern_id, likes_count=record.likes_count)


@router.delete(
    "/{pattern_id}/like", response_model=LikeResponse, dependencies=[rate_limit_dependency("patterns:unlike")]
)
async def unlike_pattern(
    pattern_id: UUID,
    user: Annotated[User | None, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db_session)] = Depends(),
) -> LikeResponse:
    record = await _get_pattern(session, pattern_id)
    liker_id = user.id if user else None
    if liker_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user required")
    existing = await session.get(PatternLike, {"pattern_id": pattern_id, "user_id": liker_id})
    if existing:
        await session.delete(existing)
        record.likes_count = max(0, record.likes_count - 1)
        await session.commit()
        await session.refresh(record)
    return LikeResponse(pattern_id=pattern_id, likes_count=record.likes_count)


@router.post("/{pattern_id}/fork", response_model=ForkResponse, dependencies=[rate_limit_dependency("patterns:fork", True)])
async def fork_pattern(
    pattern_id: UUID,
    payload: PatternCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)] = Depends(),
) -> ForkResponse:
    parent = await _get_pattern(session, pattern_id)
    forked = Pattern(
        user_id=payload.user_id,
        exhibit_type=payload.exhibit_type or parent.exhibit_type,
        title=payload.title or parent.title,
        description=payload.description or parent.description,
        parameters=payload.parameters or parent.parameters,
        seed=payload.seed or parent.seed,
        forked_from=pattern_id,
    )
    session.add(forked)
    await session.commit()
    await session.refresh(forked)
    return ForkResponse(forked_id=forked.id, parent_id=pattern_id)


@router.get("/{pattern_id}/forks", response_model=list[PatternResponse])
async def get_forks(
    pattern_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)] = Depends()
) -> list[PatternResponse]:
    stmt = select(Pattern).where(Pattern.forked_from == pattern_id).order_by(Pattern.created_at.desc())
    forks = (await session.scalars(stmt)).all()
    return [PatternResponse.model_validate(item) for item in forks]
