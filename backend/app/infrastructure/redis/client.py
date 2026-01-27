from app.core.config import settings
from redis.asyncio import Redis


def create_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis(r: Redis) -> None:
    await r.aclose()
    await r.connection_pool.disconnect()
