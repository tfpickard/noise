from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampedMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=datetime.utcnow
    )


class User(Base, TimestampedMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    username: Mapped[str | None] = mapped_column(String(50), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    password_hash: Mapped[str | None] = mapped_column(String(255))

    patterns: Mapped[list["Pattern"]] = relationship(back_populates="user")


class Pattern(Base, TimestampedMixin):
    __tablename__ = "patterns"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    exhibit_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    seed: Mapped[int | None] = mapped_column(BigInteger)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    likes_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    views_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    forked_from: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patterns.id"))

    user: Mapped[User | None] = relationship(back_populates="patterns", foreign_keys=[user_id])
    forks: Mapped[list["Pattern"]] = relationship(remote_side="Pattern.id")
    embedding: Mapped["PatternEmbedding" | None] = relationship(back_populates="pattern")
    likes: Mapped[list["PatternLike"]] = relationship(back_populates="pattern")


class PatternEmbedding(Base, TimestampedMixin):
    __tablename__ = "pattern_embeddings"

    pattern_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(128))

    pattern: Mapped[Pattern] = relationship(back_populates="embedding")


class PatternLike(Base, TimestampedMixin):
    __tablename__ = "pattern_likes"

    pattern_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    pattern: Mapped[Pattern] = relationship(back_populates="likes")


class Collection(Base, TimestampedMixin):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))


class CollectionPattern(Base, TimestampedMixin):
    __tablename__ = "collection_patterns"

    collection_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    pattern_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int | None] = mapped_column(Integer)


class AnalyticsEvent(Base, TimestampedMixin):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(50))
    pattern_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patterns.id"))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id: Mapped[str | None] = mapped_column(String(100))
    metadata: Mapped[dict | None] = mapped_column(JSON)


class CollaborationSession(Base, TimestampedMixin):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str | None] = mapped_column(String(200))
    host_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    state: Mapped[dict | None] = mapped_column(JSON)


class ExportJob(Base, TimestampedMixin):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pattern_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patterns.id"))
    status: Mapped[str] = mapped_column(String(50), default="queued", server_default=text("'queued'"))
    url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
