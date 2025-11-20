"""Analytics event tracking model."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalyticsEvent(Base):
    """Analytics event for tracking user behavior."""

    __tablename__ = "analytics_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pattern_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("patterns.id", ondelete="SET NULL")
    )
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    session_id: Mapped[str | None] = mapped_column(String(100))
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_analytics_type_time", "event_type", "created_at"),
        Index("ix_analytics_pattern", "pattern_id", "created_at"),
        Index("ix_analytics_user", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AnalyticsEvent {self.event_type}>"
