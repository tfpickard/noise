"""Pattern models for noise configurations."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Pattern(Base):
    """Saved noise pattern configuration."""

    __tablename__ = "patterns"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    exhibit_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    seed: Mapped[int | None] = mapped_column(BigInteger)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    forks_count: Mapped[int] = mapped_column(Integer, default=0)
    forked_from_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("patterns.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="patterns")
    forked_from: Mapped["Pattern | None"] = relationship(
        remote_side=[id], foreign_keys=[forked_from_id]
    )
    embedding: Mapped["PatternEmbedding | None"] = relationship(
        back_populates="pattern", cascade="all, delete-orphan", uselist=False
    )
    likes: Mapped[list["PatternLike"]] = relationship(
        back_populates="pattern", cascade="all, delete-orphan"
    )
    collection_memberships: Mapped[list["CollectionPattern"]] = relationship(
        back_populates="pattern", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_patterns_parameters_gin", "parameters", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Pattern {self.id} - {self.exhibit_type}>"


class PatternEmbedding(Base):
    """Vector embedding for pattern similarity search."""

    __tablename__ = "pattern_embeddings"

    pattern_id: Mapped[UUID] = mapped_column(
        ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    embedding: Mapped[Vector] = mapped_column(Vector(128))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    pattern: Mapped["Pattern"] = relationship(back_populates="embedding")

    __table_args__ = (
        Index(
            "ix_embeddings_vector_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PatternEmbedding {self.pattern_id}>"


class PatternLike(Base):
    """User likes/favorites for patterns."""

    __tablename__ = "pattern_likes"

    pattern_id: Mapped[UUID] = mapped_column(
        ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    pattern: Mapped["Pattern"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="pattern_likes")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PatternLike {self.user_id} -> {self.pattern_id}>"
