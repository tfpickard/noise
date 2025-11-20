from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis_client
from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_session
from app.models import User


async def get_db_session() -> AsyncSession:
    async with get_session() as session:
        yield session


def get_redis() -> Redis | None:
    return get_redis_client()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: Annotated[AsyncSession, Depends(get_db_session)] | None = None,
) -> User | None:
    if authorization is None or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split()[1]
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    user_id = payload.get("sub")
    if user_id is None or session is None:
        return None
    user = await session.get(User, UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    return user


async def enforce_rate_limit(
    scope: str,
    limit: int,
    redis: Redis | None,
    user: User | None,
) -> None:
    if redis is None:
        return
    now = int(datetime.now(timezone.utc).timestamp())
    window = now // 60
    key = f"rate:{scope}:{user.id if user else 'anon'}:{window}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    if count > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")


def rate_limit_dependency(scope: str, authenticated: bool = False) -> Depends:
    limit = (
        settings.rate_limit_authenticated_per_minute if authenticated else settings.rate_limit_anonymous_per_minute
    )

    async def dependency(
        redis: Annotated[Redis | None, Depends(get_redis)] = None,
        user: Annotated[User | None, Depends(get_current_user)] = None,
    ) -> None:
        await enforce_rate_limit(scope, limit, redis, user)

    return Depends(dependency)
