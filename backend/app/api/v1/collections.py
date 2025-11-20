from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models import Collection, CollectionPattern, Pattern
from app.schemas.collections import CollectionCreate, CollectionResponse
from app.schemas.patterns import PatternResponse

router = APIRouter()


async def _get_collection(session: AsyncSession, collection_id: UUID) -> Collection:
    collection = await session.get(Collection, collection_id)
    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


@router.post("", response_model=CollectionResponse)
async def create_collection(
    payload: CollectionCreate, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CollectionResponse:
    record = Collection(
        user_id=payload.user_id,
        title=payload.title,
        description=payload.description,
        is_featured=payload.is_featured,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return CollectionResponse.model_validate({"patterns": [], **record.__dict__})


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CollectionResponse:
    collection = await _get_collection(session, collection_id)
    stmt = (
        select(Pattern)
        .join(CollectionPattern, CollectionPattern.pattern_id == Pattern.id)
        .where(CollectionPattern.collection_id == collection_id)
        .order_by(CollectionPattern.position.nulls_last())
    )
    patterns = (await session.scalars(stmt)).all()
    return CollectionResponse.model_validate(
        {
            "id": collection.id,
            "user_id": collection.user_id,
            "title": collection.title,
            "description": collection.description,
            "is_featured": collection.is_featured,
            "created_at": collection.created_at,
            "patterns": [PatternResponse.model_validate(p) for p in patterns],
        }
    )


@router.put("/{collection_id}/patterns", response_model=CollectionResponse)
async def add_patterns(
    collection_id: UUID,
    pattern_ids: list[UUID],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CollectionResponse:
    await _get_collection(session, collection_id)
    for index, pid in enumerate(pattern_ids):
        link = CollectionPattern(collection_id=collection_id, pattern_id=pid, position=index)
        session.merge(link)
    await session.commit()
    return await get_collection(collection_id, session)


@router.get("/featured", response_model=list[CollectionResponse])
async def featured_collections(session: Annotated[AsyncSession, Depends(get_db_session)]) -> list[CollectionResponse]:
    featured = (await session.scalars(select(Collection).where(Collection.is_featured == True))).all()  # noqa: E712
    return [await get_collection(c.id, session) for c in featured]
