"""Redis cache utilities."""

import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

# Redis connection pool
redis_pool: aioredis.ConnectionPool | None = None
redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance."""
    global redis_client, redis_pool
    if redis_client is None:
        redis_pool = aioredis.ConnectionPool.from_url(
            str(settings.redis_url),
            decode_responses=True,
            max_connections=50,
        )
        redis_client = aioredis.Redis(connection_pool=redis_pool)
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client, redis_pool
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    redis_client = None
    redis_pool = None


class RedisCache:
    """Redis cache helper with JSON serialization."""

    def __init__(self, prefix: str = "noise_museum") -> None:
        """Initialize cache with prefix."""
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        client = await get_redis()
        value = await client.get(self._make_key(key))
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> None:
        """Set value in cache with optional TTL."""
        client = await get_redis()
        ttl = ttl or settings.redis_cache_ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await client.setex(self._make_key(key), ttl, serialized)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        client = await get_redis()
        await client.delete(self._make_key(key))

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = await get_redis()
        return bool(await client.exists(self._make_key(key)))

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        client = await get_redis()
        return await client.incrby(self._make_key(key), amount)

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        if not keys:
            return {}
        client = await get_redis()
        prefixed_keys = [self._make_key(k) for k in keys]
        values = await client.mget(prefixed_keys)
        result = {}
        for key, value in zip(keys, values, strict=False):
            if value is not None:
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
        return result

    async def set_many(
        self, mapping: dict[str, Any], ttl: int | None = None
    ) -> None:
        """Set multiple values in cache."""
        if not mapping:
            return
        client = await get_redis()
        ttl = ttl or settings.redis_cache_ttl
        pipe = client.pipeline()
        for key, value in mapping.items():
            serialized = json.dumps(value) if not isinstance(value, str) else value
            pipe.setex(self._make_key(key), ttl, serialized)
        await pipe.execute()


# Global cache instance
cache = RedisCache()
