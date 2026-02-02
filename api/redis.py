from redis.asyncio import Redis, ConnectionPool

from api.config import settings

pool: ConnectionPool | None = None


async def init_redis() -> None:
    global pool
    pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    global pool
    if pool is not None:
        await pool.aclose()
        pool = None


def get_redis() -> Redis:
    if pool is None:
        raise RuntimeError("Redis connection pool is not initialized")
    return Redis(connection_pool=pool)
