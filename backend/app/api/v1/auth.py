from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, rate_limit_dependency
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.auth import TokenPair, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, dependencies=[rate_limit_dependency("auth:register")])
async def register(payload: UserCreate, session: Annotated[AsyncSession, Depends(get_db_session)]) -> UserResponse:
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
    user = User(
        email=payload.email,
        username=payload.username or payload.email.split("@")[0],
        display_name=payload.username or payload.email,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair, dependencies=[rate_limit_dependency("auth:login")])
async def login(payload: UserCreate, session: Annotated[AsyncSession, Depends(get_db_session)]) -> TokenPair:
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=timedelta(minutes=15))


@router.post("/refresh", response_model=TokenPair, dependencies=[rate_limit_dependency("auth:refresh")])
async def refresh(refresh_token: Annotated[str, Body(embed=True)]) -> TokenPair:
    decoded = decode_token(refresh_token)
    if decoded.get("scope") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
    subject = decoded.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
    access_token = create_access_token(subject)
    new_refresh = create_refresh_token(subject)
    return TokenPair(access_token=access_token, refresh_token=new_refresh, expires_in=timedelta(minutes=15))


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User | None, Depends(get_current_user)] = None) -> UserResponse:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    return UserResponse.model_validate(user)
