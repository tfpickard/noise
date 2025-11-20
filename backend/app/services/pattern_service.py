"""Service for pattern business logic."""

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache
from app.models.pattern import Pattern, PatternEmbedding, PatternLike
from app.schemas.pattern import PatternCreate, PatternUpdate
from app.services.embedding_service import embedding_service


class PatternService:
    """Business logic for pattern management."""

    @staticmethod
    async def create_pattern(
        db: AsyncSession, pattern_data: PatternCreate, user_id: UUID | None = None
    ) -> Pattern:
        """Create a new pattern."""
        pattern = Pattern(
            user_id=user_id,
            exhibit_type=pattern_data.exhibit_type,
            title=pattern_data.title,
            description=pattern_data.description,
            parameters=pattern_data.parameters,
            seed=pattern_data.seed,
            is_public=pattern_data.is_public,
        )

        db.add(pattern)
        await db.flush()

        # Generate embedding
        embedding_vector = embedding_service.generate_embedding(
            pattern_data.parameters, pattern_data.exhibit_type
        )
        embedding = PatternEmbedding(
            pattern_id=pattern.id, embedding=embedding_vector
        )
        db.add(embedding)

        await db.commit()
        await db.refresh(pattern)

        # Invalidate cache
        await cache.delete(f"pattern:{pattern.id}")

        return pattern

    @staticmethod
    async def get_pattern(db: AsyncSession, pattern_id: UUID) -> Pattern | None:
        """Get pattern by ID with caching."""
        # Try cache first
        cached = await cache.get(f"pattern:{pattern_id}")
        if cached:
            # Fetch from DB to get full object
            pass

        result = await db.execute(
            select(Pattern)
            .where(Pattern.id == pattern_id)
            .options(selectinload(Pattern.embedding))
        )
        pattern = result.scalar_one_or_none()

        if pattern:
            # Increment view count asynchronously
            pattern.views_count += 1
            await db.commit()

        return pattern

    @staticmethod
    async def update_pattern(
        db: AsyncSession, pattern_id: UUID, pattern_data: PatternUpdate
    ) -> Pattern | None:
        """Update pattern."""
        result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
        pattern = result.scalar_one_or_none()

        if not pattern:
            return None

        update_data = pattern_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pattern, field, value)

        # Regenerate embedding if parameters changed
        if "parameters" in update_data:
            embedding_vector = embedding_service.generate_embedding(
                pattern.parameters, pattern.exhibit_type
            )

            # Update or create embedding
            result = await db.execute(
                select(PatternEmbedding).where(
                    PatternEmbedding.pattern_id == pattern_id
                )
            )
            embedding = result.scalar_one_or_none()

            if embedding:
                embedding.embedding = embedding_vector
            else:
                embedding = PatternEmbedding(
                    pattern_id=pattern_id, embedding=embedding_vector
                )
                db.add(embedding)

        await db.commit()
        await db.refresh(pattern)

        # Invalidate cache
        await cache.delete(f"pattern:{pattern_id}")

        return pattern

    @staticmethod
    async def delete_pattern(db: AsyncSession, pattern_id: UUID) -> bool:
        """Delete pattern."""
        result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
        pattern = result.scalar_one_or_none()

        if not pattern:
            return False

        await db.delete(pattern)
        await db.commit()

        # Invalidate cache
        await cache.delete(f"pattern:{pattern_id}")

        return True

    @staticmethod
    async def list_patterns(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        exhibit_type: str | None = None,
        user_id: UUID | None = None,
        public_only: bool = True,
    ) -> tuple[list[Pattern], int]:
        """List patterns with pagination."""
        query = select(Pattern)

        if exhibit_type:
            query = query.where(Pattern.exhibit_type == exhibit_type)
        if user_id:
            query = query.where(Pattern.user_id == user_id)
        if public_only:
            query = query.where(Pattern.is_public == True)  # noqa: E712

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(desc(Pattern.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        patterns = result.scalars().all()

        return list(patterns), total

    @staticmethod
    async def fork_pattern(
        db: AsyncSession,
        pattern_id: UUID,
        user_id: UUID | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> Pattern | None:
        """Fork/remix a pattern."""
        # Get original pattern
        result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
        original = result.scalar_one_or_none()

        if not original:
            return None

        # Create forked pattern
        forked = Pattern(
            user_id=user_id,
            exhibit_type=original.exhibit_type,
            title=title or f"Fork of {original.title or 'Untitled'}",
            description=description or original.description,
            parameters=original.parameters.copy(),
            seed=original.seed,
            is_public=True,
            forked_from_id=original.id,
        )

        db.add(forked)
        await db.flush()

        # Copy embedding
        if original.embedding:
            forked_embedding = PatternEmbedding(
                pattern_id=forked.id, embedding=original.embedding.embedding
            )
            db.add(forked_embedding)

        # Increment fork count on original
        original.forks_count += 1

        await db.commit()
        await db.refresh(forked)

        return forked

    @staticmethod
    async def like_pattern(
        db: AsyncSession, pattern_id: UUID, user_id: UUID
    ) -> bool:
        """Like a pattern."""
        # Check if already liked
        result = await db.execute(
            select(PatternLike).where(
                PatternLike.pattern_id == pattern_id, PatternLike.user_id == user_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return False

        # Create like
        like = PatternLike(pattern_id=pattern_id, user_id=user_id)
        db.add(like)

        # Increment likes count
        result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
        pattern = result.scalar_one_or_none()
        if pattern:
            pattern.likes_count += 1

        await db.commit()
        await cache.delete(f"pattern:{pattern_id}")

        return True

    @staticmethod
    async def unlike_pattern(
        db: AsyncSession, pattern_id: UUID, user_id: UUID
    ) -> bool:
        """Unlike a pattern."""
        result = await db.execute(
            select(PatternLike).where(
                PatternLike.pattern_id == pattern_id, PatternLike.user_id == user_id
            )
        )
        like = result.scalar_one_or_none()

        if not like:
            return False

        await db.delete(like)

        # Decrement likes count
        result = await db.execute(select(Pattern).where(Pattern.id == pattern_id))
        pattern = result.scalar_one_or_none()
        if pattern:
            pattern.likes_count = max(0, pattern.likes_count - 1)

        await db.commit()
        await cache.delete(f"pattern:{pattern_id}")

        return True

    @staticmethod
    async def get_trending_patterns(
        db: AsyncSession, limit: int = 10, cache_ttl: int = 300
    ) -> list[Pattern]:
        """Get trending patterns (cached)."""
        cache_key = f"trending_patterns:{limit}"
        cached = await cache.get(cache_key)

        if cached:
            # Fetch patterns by IDs
            pattern_ids = [UUID(pid) for pid in cached]
            result = await db.execute(
                select(Pattern).where(Pattern.id.in_(pattern_ids))
            )
            return list(result.scalars().all())

        # Calculate trending score: weighted combination of recent likes, views, forks
        # Simple algorithm: likes * 3 + views * 0.5 + forks * 5
        query = (
            select(Pattern)
            .where(Pattern.is_public == True)  # noqa: E712
            .order_by(
                desc(
                    Pattern.likes_count * 3
                    + Pattern.views_count * 0.5
                    + Pattern.forks_count * 5
                )
            )
            .limit(limit)
        )

        result = await db.execute(query)
        patterns = list(result.scalars().all())

        # Cache pattern IDs
        pattern_ids = [str(p.id) for p in patterns]
        await cache.set(cache_key, pattern_ids, ttl=cache_ttl)

        return patterns


pattern_service = PatternService()
