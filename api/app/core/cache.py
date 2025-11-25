"""
Redis caching utilities.
"""

from aioredis import Redis
from app.core.config import settings

redis = Redis.from_url(settings.REDIS_URL)

async def get_cached(key: str):
    return await redis.get(key)

async def set_cached(key: str, value: str, ttl: int = 300):
    await redis.setex(key, ttl, value)