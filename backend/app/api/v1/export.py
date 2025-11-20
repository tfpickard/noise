from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models import ExportJob
from app.schemas.export import RenderRequest, RenderResponse

router = APIRouter()


@router.post("/render", response_model=RenderResponse)
async def render(payload: RenderRequest, session: Annotated[AsyncSession, Depends(get_db_session)]) -> RenderResponse:
    job = ExportJob(pattern_id=str(payload.pattern_id), status="queued", notes=payload.note)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return RenderResponse.model_validate(job)


@router.get("/{export_id}", response_model=RenderResponse)
async def get_export(export_id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)]) -> RenderResponse:
    job = await session.get(ExportJob, export_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return RenderResponse.model_validate(job)


@router.post("/video", response_model=RenderResponse)
async def render_video(payload: RenderRequest, session: Annotated[AsyncSession, Depends(get_db_session)]) -> RenderResponse:
    job = ExportJob(pattern_id=str(payload.pattern_id), status="queued", notes=payload.note)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return RenderResponse.model_validate(job)
