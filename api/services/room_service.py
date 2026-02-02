import json
import uuid
from datetime import datetime, timezone

from redis.asyncio import Redis

from api.config import settings
from api.models import RoomResponse


def _room_key(room_id: str) -> str:
    return f"room:{room_id}"


async def create_room(redis: Redis) -> RoomResponse:
    room_id = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    ttl = settings.ROOM_TTL_SECONDS
    expires_at = datetime.fromtimestamp(now.timestamp() + ttl, tz=timezone.utc)

    room_data = {
        "room_id": room_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    await redis.set(_room_key(room_id), json.dumps(room_data), ex=ttl)

    return RoomResponse(
        room_id=room_id,
        created_at=now,
        expires_at=expires_at,
        ttl_seconds=ttl,
    )


async def get_room(redis: Redis, room_id: str) -> RoomResponse | None:
    raw = await redis.get(_room_key(room_id))
    if raw is None:
        return None

    data = json.loads(raw)
    ttl = await redis.ttl(_room_key(room_id))

    return RoomResponse(
        room_id=data["room_id"],
        created_at=datetime.fromisoformat(data["created_at"]),
        expires_at=datetime.fromisoformat(data["expires_at"]),
        ttl_seconds=max(ttl, 0),
    )


async def room_exists(redis: Redis, room_id: str) -> bool:
    return await redis.exists(_room_key(room_id)) > 0


async def delete_room(redis: Redis, room_id: str) -> None:
    await redis.delete(
        _room_key(room_id),
        f"room:{room_id}:messages",
    )
