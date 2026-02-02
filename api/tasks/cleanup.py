import asyncio

from api.config import settings
from api.redis import get_redis
from api.services.chat_service import manager
from api.services.room_service import room_exists


async def cleanup_expired_rooms() -> None:
    while True:
        await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)
        try:
            redis = get_redis()
            for room_id in manager.get_room_ids():
                if not await room_exists(redis, room_id):
                    await manager.disconnect_room(room_id)
        except Exception:
            pass
