import json
import redis.asyncio as aioredis
from typing import Optional, AsyncGenerator
from app.config import settings

_redis_pool: Optional[aioredis.Redis] = None


async def get_redis_pool() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client = await get_redis_pool()
    yield client


async def publish_alert(alert_data: dict) -> None:
    client = await get_redis_pool()
    await client.publish("catguard:alerts", json.dumps(alert_data))


async def set_cache(key: str, value: dict, expire: int = 300) -> None:
    client = await get_redis_pool()
    await client.setex(f"cache:{key}", expire, json.dumps(value))


async def get_cache(key: str) -> Optional[dict]:
    client = await get_redis_pool()
    data = await client.get(f"cache:{key}")
    return json.loads(data) if data else None


async def delete_cache(key: str) -> None:
    client = await get_redis_pool()
    await client.delete(f"cache:{key}")


async def blacklist_token(jti: str, expire_seconds: int) -> None:
    client = await get_redis_pool()
    await client.setex(f"blacklist:{jti}", expire_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    client = await get_redis_pool()
    return await client.exists(f"blacklist:{jti}") == 1


async def close_redis() -> None:
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
