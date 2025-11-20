from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import TokenPair, UserCreate, UserResponse
from app.services.inmemory_store import store

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(payload: UserCreate) -> UserResponse:
    user_id = uuid4()
    record = {
        "id": user_id,
        "email": payload.email,
        "username": payload.username,
        "display_name": payload.username,
        "created_at": datetime.now(timezone.utc),
    }
    store.collections.setdefault("users", {})[user_id] = record
    return UserResponse.model_validate(record)


@router.post("/login", response_model=TokenPair)
async def login(payload: UserCreate) -> TokenPair:
    if payload.email not in [u.get("email") for u in store.collections.get("users", {}).values()]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    expires = timedelta(minutes=15)
    return TokenPair(access_token="dummy-access", refresh_token="dummy-refresh", expires_in=expires)


@router.post("/refresh", response_model=TokenPair)
async def refresh() -> TokenPair:
    return TokenPair(access_token="dummy-access", refresh_token="dummy-refresh", expires_in=timedelta(minutes=15))


@router.get("/me", response_model=UserResponse)
async def me() -> UserResponse:
    users = store.collections.get("users", {})
    first = next(iter(users.values()), None)
    if first is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no users")
    return UserResponse.model_validate(first)
