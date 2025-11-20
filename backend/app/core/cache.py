from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None = None


def get_redis_client() -> Redis | None:
    global redis_client
    if redis_client is None and settings.redis_url:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


@asynccontextmanager
async def redis_context() -> AsyncIterator[Redis]:
    client = get_redis_client()
    if client is None:
        raise RuntimeError("Redis is not configured. Set REDIS_URL.")
    try:
        yield client
    finally:
        await client.aclose()
