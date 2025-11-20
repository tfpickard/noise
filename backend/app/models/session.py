"""Collaboration session model for real-time features."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CollaborationSession(Base):
    """Real-time collaboration session."""

    __tablename__ = "collaboration_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    pattern_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("patterns.id", ondelete="SET NULL")
    )
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    current_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    max_participants: Mapped[int] = mapped_column(default=10)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column()
    last_activity_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return f"<CollaborationSession {self.session_code}>"
