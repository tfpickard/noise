"""Collaboration session API endpoints."""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DatabaseSession
from app.core.security import create_session_code
from app.models.session import CollaborationSession
from app.schemas.session import (
    CollaborationSession as SessionSchema,
    SessionCreate,
    SessionMessage,
)

router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for collaboration sessions."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, session_code: str, websocket: WebSocket) -> None:
        """Add connection to session."""
        await websocket.accept()
        if session_code not in self.active_connections:
            self.active_connections[session_code] = []
        self.active_connections[session_code].append(websocket)

    def disconnect(self, session_code: str, websocket: WebSocket) -> None:
        """Remove connection from session."""
        if session_code in self.active_connections:
            self.active_connections[session_code].remove(websocket)
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]

    async def broadcast(
        self, session_code: str, message: dict, exclude: WebSocket | None = None
    ) -> None:
        """Broadcast message to all connections in session."""
        if session_code in self.active_connections:
            for connection in self.active_connections[session_code]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        # Connection closed, remove it
                        self.disconnect(session_code, connection)

    def get_participant_count(self, session_code: str) -> int:
        """Get number of active participants."""
        return len(self.active_connections.get(session_code, []))


manager = ConnectionManager()


@router.post("/", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CollaborationSession:
    """Create a new collaboration session."""
    # Generate unique session code
    session_code = create_session_code()

    # Check uniqueness
    while True:
        result = await db.execute(
            select(CollaborationSession).where(
                CollaborationSession.session_code == session_code
            )
        )
        if not result.scalar_one_or_none():
            break
        session_code = create_session_code()

    # Create session
    expires_at = datetime.utcnow() + timedelta(hours=session_data.expires_in_hours)

    session = CollaborationSession(
        session_code=session_code,
        pattern_id=session_data.pattern_id,
        owner_id=current_user.id if current_user else None,
        max_participants=session_data.max_participants,
        expires_at=expires_at,
        is_active=True,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.get("/{session_id}", response_model=SessionSchema)
async def get_session(
    session_id: UUID,
    db: DatabaseSession,
) -> CollaborationSession:
    """Get session details."""
    result = await db.execute(
        select(CollaborationSession).where(CollaborationSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    return session


@router.get("/code/{session_code}", response_model=SessionSchema)
async def get_session_by_code(
    session_code: str,
    db: DatabaseSession,
) -> CollaborationSession:
    """Get session by code."""
    result = await db.execute(
        select(CollaborationSession).where(
            CollaborationSession.session_code == session_code
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Session is no longer active"
        )

    if session.expires_at and session.expires_at < datetime.utcnow():
        session.is_active = False
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Session has expired"
        )

    return session


@router.websocket("/ws/{session_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_code: str,
) -> None:
    """WebSocket endpoint for real-time collaboration."""
    # Note: In production, validate session and user here
    await manager.connect(session_code, websocket)

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "session_code": session_code,
                "participant_count": manager.get_participant_count(session_code),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Notify others of new participant
        await manager.broadcast(
            session_code,
            {
                "type": "participant_joined",
                "participant_count": manager.get_participant_count(session_code),
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude=websocket,
        )

        # Listen for messages
        while True:
            data = await websocket.receive_json()

            # Broadcast to other participants
            message = {
                **data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await manager.broadcast(session_code, message, exclude=websocket)

    except WebSocketDisconnect:
        manager.disconnect(session_code, websocket)

        # Notify others of participant leaving
        await manager.broadcast(
            session_code,
            {
                "type": "participant_left",
                "participant_count": manager.get_participant_count(session_code),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(
    session_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """End a collaboration session (owner only)."""
    result = await db.execute(
        select(CollaborationSession).where(CollaborationSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if current_user and session.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to end this session",
        )

    session.is_active = False
    await db.commit()
