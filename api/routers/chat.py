from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.redis import get_redis
from api.services.chat_service import manager
from api.services.room_service import room_exists

router = APIRouter(tags=["chat"])


@router.websocket("/ws/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: str) -> None:
    redis = get_redis()

    if not await room_exists(redis, room_id):
        await websocket.close(code=4004, reason="Room not found or expired")
        return

    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
