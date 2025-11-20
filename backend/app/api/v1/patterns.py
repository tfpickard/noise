"""Pattern API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DatabaseSession
from app.core.cache import cache
from app.models.pattern import Pattern, PatternEmbedding
from app.schemas.pattern import (
    Pattern as PatternSchema,
    PatternCreate,
    PatternFork,
    PatternList,
    PatternUpdate,
    SimilaritySearch,
)
from app.services.embedding_service import embedding_service
from app.services.pattern_service import pattern_service

router = APIRouter()


@router.post("/", response_model=PatternSchema, status_code=status.HTTP_201_CREATED)
async def create_pattern(
    pattern_data: PatternCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Pattern:
    """Create a new pattern."""
    user_id = current_user.id if current_user else None
    return await pattern_service.create_pattern(db, pattern_data, user_id)


@router.get("/{pattern_id}", response_model=PatternSchema)
async def get_pattern(
    pattern_id: UUID,
    db: DatabaseSession,
) -> Pattern:
    """Get pattern by ID."""
    pattern = await pattern_service.get_pattern(db, pattern_id)
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )
    return pattern


@router.put("/{pattern_id}", response_model=PatternSchema)
async def update_pattern(
    pattern_id: UUID,
    pattern_data: PatternUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Pattern:
    """Update pattern (owner only)."""
    # Get existing pattern
    result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    # Check ownership (allow if no user or user is owner)
    if current_user and existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this pattern",
        )

    pattern = await pattern_service.update_pattern(db, pattern_id, pattern_data)
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    return pattern


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern(
    pattern_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """Delete pattern (owner only)."""
    # Get existing pattern
    result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    # Check ownership
    if current_user and existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this pattern",
        )

    await pattern_service.delete_pattern(db, pattern_id)


@router.get("/", response_model=PatternList)
async def list_patterns(
    db: DatabaseSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    exhibit_type: str | None = None,
    user_id: UUID | None = None,
) -> PatternList:
    """List patterns with pagination."""
    patterns, total = await pattern_service.list_patterns(
        db, skip=skip, limit=limit, exhibit_type=exhibit_type, user_id=user_id
    )

    return PatternList(
        items=patterns,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/discover/feed", response_model=PatternList)
async def discover_patterns(
    db: DatabaseSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PatternList:
    """Discover feed of public patterns."""
    patterns, total = await pattern_service.list_patterns(
        db, skip=skip, limit=limit, public_only=True
    )

    return PatternList(
        items=patterns,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/trending/top", response_model=list[PatternSchema])
async def get_trending_patterns(
    db: DatabaseSession,
    limit: int = Query(10, ge=1, le=50),
) -> list[Pattern]:
    """Get trending patterns."""
    return await pattern_service.get_trending_patterns(db, limit)


@router.post("/{pattern_id}/fork", response_model=PatternSchema)
async def fork_pattern(
    pattern_id: UUID,
    fork_data: PatternFork,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Pattern:
    """Fork/remix a pattern."""
    user_id = current_user.id if current_user else None
    pattern = await pattern_service.fork_pattern(
        db,
        pattern_id,
        user_id=user_id,
        title=fork_data.title,
        description=fork_data.description,
    )

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    return pattern


@router.get("/{pattern_id}/forks", response_model=list[PatternSchema])
async def get_pattern_forks(
    pattern_id: UUID,
    db: DatabaseSession,
    limit: int = Query(20, ge=1, le=100),
) -> list[Pattern]:
    """Get patterns forked from this pattern."""
    result = await db.execute(
        select(Pattern)
        .where(Pattern.forked_from_id == pattern_id)
        .order_by(desc(Pattern.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


@router.post("/{pattern_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_pattern(
    pattern_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """Like a pattern."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to like patterns",
        )

    success = await pattern_service.like_pattern(db, pattern_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pattern already liked or not found",
        )


@router.delete("/{pattern_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_pattern(
    pattern_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """Unlike a pattern."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    success = await pattern_service.unlike_pattern(db, pattern_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )


@router.post("/similar", response_model=list[PatternSchema])
async def find_similar_patterns(
    search: SimilaritySearch,
    db: DatabaseSession,
) -> list[Pattern]:
    """Find similar patterns using vector similarity."""
    # Get query embedding
    if search.pattern_id:
        # Use existing pattern's embedding
        result = await db.execute(
            select(PatternEmbedding).where(
                PatternEmbedding.pattern_id == search.pattern_id
            )
        )
        embedding_obj = result.scalar_one_or_none()
        if not embedding_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pattern embedding not found",
            )
        query_embedding = embedding_obj.embedding
    elif search.embedding:
        query_embedding = search.embedding
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either pattern_id or embedding must be provided",
        )

    # Use pgvector cosine similarity search
    # Note: In a real implementation with pgvector installed:
    # from pgvector.sqlalchemy import Vector
    # result = await db.execute(
    #     select(Pattern, PatternEmbedding.embedding.cosine_distance(query_embedding))
    #     .join(PatternEmbedding)
    #     .where(PatternEmbedding.embedding.cosine_distance(query_embedding) < (1 - search.threshold))
    #     .order_by(PatternEmbedding.embedding.cosine_distance(query_embedding))
    #     .limit(search.limit)
    # )

    # Simplified version without pgvector operators
    result = await db.execute(
        select(Pattern)
        .join(PatternEmbedding)
        .where(Pattern.is_public == True)  # noqa: E712
        .options(selectinload(Pattern.embedding))
        .limit(search.limit * 5)  # Get more to filter
    )
    all_patterns = list(result.scalars().all())

    # Calculate similarities in Python (not efficient, but works without pgvector)
    similarities = []
    for pattern in all_patterns:
        if pattern.embedding:
            similarity = embedding_service.compute_similarity(
                query_embedding, pattern.embedding.embedding
            )
            if similarity >= search.threshold:
                similarities.append((pattern, similarity))

    # Sort by similarity and limit
    similarities.sort(key=lambda x: x[1], reverse=True)
    similar_patterns = [p for p, _ in similarities[: search.limit]]

    return similar_patterns


@router.post("/{pattern_id}/embedding", response_model=dict)
async def generate_pattern_embedding(
    pattern_id: UUID,
    db: DatabaseSession,
) -> dict:
    """Regenerate embedding for a pattern."""
    result = await db.execute(
        select(Pattern).where(Pattern.id == pattern_id).options(
            selectinload(Pattern.embedding)
        )
    )
    pattern = result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    # Generate new embedding
    embedding_vector = embedding_service.generate_embedding(
        pattern.parameters, pattern.exhibit_type
    )

    # Update or create embedding
    if pattern.embedding:
        pattern.embedding.embedding = embedding_vector
    else:
        embedding = PatternEmbedding(pattern_id=pattern_id, embedding=embedding_vector)
        db.add(embedding)

    await db.commit()

    return {"pattern_id": str(pattern_id), "embedding_updated": True}
