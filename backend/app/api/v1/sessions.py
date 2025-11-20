from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.sessions import SessionCreate, SessionResponse
from app.services.inmemory_store import store

router = APIRouter()


def _get_session(session_id: UUID) -> dict:
    session = store.sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("", response_model=SessionResponse)
async def create_session(payload: SessionCreate) -> SessionResponse:
    record = store.create_session(payload.model_dump())
    return SessionResponse.model_validate(record)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID) -> SessionResponse:
    session = _get_session(session_id)
    return SessionResponse.model_validate(session)
