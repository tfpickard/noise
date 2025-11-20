from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.collections import CollectionCreate, CollectionResponse
from app.schemas.patterns import PatternResponse
from app.services.inmemory_store import store

router = APIRouter()


def _ensure_collection(collection_id: UUID) -> dict:
    collection = store.collections.get(collection_id)
    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


@router.post("", response_model=CollectionResponse)
async def create_collection(payload: CollectionCreate) -> CollectionResponse:
    record = store.create_collection(payload.model_dump())
    return CollectionResponse.model_validate({**record, "patterns": []})


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: UUID) -> CollectionResponse:
    collection = _ensure_collection(collection_id)
    patterns = [store.patterns[p_id] for p_id in store.collection_patterns.get(collection_id, []) if p_id in store.patterns]
    return CollectionResponse.model_validate({**collection, "patterns": [PatternResponse.model_validate(p) for p in patterns]})


@router.put("/{collection_id}/patterns", response_model=CollectionResponse)
async def add_patterns(collection_id: UUID, pattern_ids: list[UUID]) -> CollectionResponse:
    _ensure_collection(collection_id)
    store.add_to_collection(collection_id, pattern_ids)
    return await get_collection(collection_id)


@router.get("/featured", response_model=list[CollectionResponse])
async def featured_collections() -> list[CollectionResponse]:
    featured = [c for c in store.collections.values() if c.get("is_featured")]
    return [await get_collection(c["id"]) for c in featured]
