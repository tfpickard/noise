"""Collection models for curated pattern galleries."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Collection(Base):
    """Curated collection of patterns."""

    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="collections")
    patterns: Mapped[list["CollectionPattern"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionPattern.position",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Collection {self.title}>"


class CollectionPattern(Base):
    """Association between collections and patterns."""

    __tablename__ = "collection_patterns"

    collection_id: Mapped[UUID] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    pattern_id: Mapped[UUID] = mapped_column(
        ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    collection: Mapped["Collection"] = relationship(back_populates="patterns")
    pattern: Mapped["Pattern"] = relationship(back_populates="collection_memberships")

    def __repr__(self) -> str:
        """String representation."""
        return f"<CollectionPattern {self.collection_id} -> {self.pattern_id}>"
