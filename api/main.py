import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from api.redis import init_redis, close_redis
from api.routers import rooms, chat
from api.tasks.cleanup import cleanup_expired_rooms


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_redis()
    cleanup_task = asyncio.create_task(cleanup_expired_rooms())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await close_redis()


app = FastAPI(title="Chatty", version="0.1.0", lifespan=lifespan)

app.include_router(rooms.router)
app.include_router(chat.router)
