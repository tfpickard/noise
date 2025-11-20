from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.export import RenderRequest, RenderResponse
from app.services.inmemory_store import store

router = APIRouter()


def _get_export(export_id: UUID) -> dict:
    export = store.exports.get(export_id)
    if export is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return export


@router.post("/render", response_model=RenderResponse)
async def render(payload: RenderRequest) -> RenderResponse:
    export = store.create_export(payload.model_dump())
    return RenderResponse.model_validate(export)


@router.get("/{export_id}", response_model=RenderResponse)
async def get_export(export_id: UUID) -> RenderResponse:
    export = _get_export(export_id)
    return RenderResponse.model_validate(export)


@router.post("/video", response_model=RenderResponse)
async def render_video(payload: RenderRequest) -> RenderResponse:
    export = store.create_export({**payload.model_dump(), "type": "video"})
    return RenderResponse.model_validate(export)
