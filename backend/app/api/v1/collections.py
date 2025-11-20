"""Collection API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, CurrentUserRequired, DatabaseSession
from app.models.collection import Collection, CollectionPattern
from app.schemas.collection import (
    Collection as CollectionSchema,
    CollectionCreate,
    CollectionPatternAdd,
    CollectionUpdate,
    CollectionWithPatterns,
)

router = APIRouter()


@router.post(
    "/", response_model=CollectionSchema, status_code=status.HTTP_201_CREATED
)
async def create_collection(
    collection_data: CollectionCreate,
    db: DatabaseSession,
    current_user: CurrentUserRequired,
) -> Collection:
    """Create a new collection."""
    collection = Collection(
        user_id=current_user.id,
        title=collection_data.title,
        description=collection_data.description,
        is_public=collection_data.is_public,
    )

    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return collection


@router.get("/{collection_id}", response_model=CollectionWithPatterns)
async def get_collection(
    collection_id: UUID,
    db: DatabaseSession,
) -> Collection:
    """Get collection with patterns."""
    result = await db.execute(
        select(Collection)
        .where(Collection.id == collection_id)
        .options(selectinload(Collection.patterns))
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )

    # Load pattern details
    collection_dict = {
        "id": collection.id,
        "user_id": collection.user_id,
        "title": collection.title,
        "description": collection.description,
        "is_public": collection.is_public,
        "is_featured": collection.is_featured,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
        "pattern_count": len(collection.patterns),
        "patterns": [cp.pattern for cp in collection.patterns],
    }

    return CollectionWithPatterns(**collection_dict)


@router.put("/{collection_id}", response_model=CollectionSchema)
async def update_collection(
    collection_id: UUID,
    collection_data: CollectionUpdate,
    db: DatabaseSession,
    current_user: CurrentUserRequired,
) -> Collection:
    """Update collection (owner only)."""
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )

    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this collection",
        )

    update_data = collection_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)

    await db.commit()
    await db.refresh(collection)

    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUserRequired,
) -> None:
    """Delete collection (owner only)."""
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )

    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this collection",
        )

    await db.delete(collection)
    await db.commit()


@router.put("/{collection_id}/patterns", response_model=CollectionSchema)
async def add_patterns_to_collection(
    collection_id: UUID,
    pattern_data: CollectionPatternAdd,
    db: DatabaseSession,
    current_user: CurrentUserRequired,
) -> Collection:
    """Add patterns to collection."""
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )

    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this collection",
        )

    # Get current max position
    result = await db.execute(
        select(func.max(CollectionPattern.position)).where(
            CollectionPattern.collection_id == collection_id
        )
    )
    max_position = result.scalar_one_or_none() or 0

    # Add patterns
    for i, pattern_id in enumerate(pattern_data.pattern_ids):
        # Check if already in collection
        result = await db.execute(
            select(CollectionPattern).where(
                CollectionPattern.collection_id == collection_id,
                CollectionPattern.pattern_id == pattern_id,
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            collection_pattern = CollectionPattern(
                collection_id=collection_id,
                pattern_id=pattern_id,
                position=max_position + i + 1,
            )
            db.add(collection_pattern)

    await db.commit()
    await db.refresh(collection)

    return collection


@router.delete(
    "/{collection_id}/patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_pattern_from_collection(
    collection_id: UUID,
    pattern_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUserRequired,
) -> None:
    """Remove pattern from collection."""
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found"
        )

    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this collection",
        )

    result = await db.execute(
        select(CollectionPattern).where(
            CollectionPattern.collection_id == collection_id,
            CollectionPattern.pattern_id == pattern_id,
        )
    )
    collection_pattern = result.scalar_one_or_none()

    if not collection_pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern not in collection",
        )

    await db.delete(collection_pattern)
    await db.commit()


@router.get("/featured/list", response_model=list[CollectionWithPatterns])
async def get_featured_collections(
    db: DatabaseSession,
    limit: int = Query(10, ge=1, le=50),
) -> list[Collection]:
    """Get featured collections."""
    result = await db.execute(
        select(Collection)
        .where(Collection.is_featured == True, Collection.is_public == True)  # noqa: E712
        .options(selectinload(Collection.patterns))
        .order_by(desc(Collection.created_at))
        .limit(limit)
    )
    collections = list(result.scalars().all())

    # Transform to include pattern details
    return [
        CollectionWithPatterns(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            description=c.description,
            is_public=c.is_public,
            is_featured=c.is_featured,
            created_at=c.created_at,
            updated_at=c.updated_at,
            pattern_count=len(c.patterns),
            patterns=[cp.pattern for cp in c.patterns],
        )
        for c in collections
    ]


@router.get("/user/{user_id}", response_model=list[CollectionSchema])
async def get_user_collections(
    user_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[Collection]:
    """Get user's collections."""
    query = select(Collection).where(Collection.user_id == user_id)

    # If not the owner, only show public collections
    if not current_user or current_user.id != user_id:
        query = query.where(Collection.is_public == True)  # noqa: E712

    query = query.order_by(desc(Collection.created_at))
    result = await db.execute(query)
    collections = list(result.scalars().all())

    return [
        CollectionSchema(
            **c.__dict__,
            pattern_count=len(await db.execute(
                select(func.count()).where(
                    CollectionPattern.collection_id == c.id
                )
            )).scalar_one()
        )
        for c in collections
    ]
