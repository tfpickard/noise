from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models import CollaborationSession
from app.schemas.sessions import SessionCreate, SessionResponse

router = APIRouter()


async def _get_session_record(session: AsyncSession, session_id: UUID) -> CollaborationSession:
    record = await session.get(CollaborationSession, session_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return record


@router.post("", response_model=SessionResponse)
async def create_session(
    payload: SessionCreate, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> SessionResponse:
    record = CollaborationSession(title=payload.title, host_id=payload.host_id, state=payload.state)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return SessionResponse.model_validate(record)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]) -> SessionResponse:
    record = await _get_session_record(session, session_id)
    return SessionResponse.model_validate(record)
