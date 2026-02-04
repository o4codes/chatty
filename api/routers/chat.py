from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.redis import get_redis
from api.services.chat_service import manager
from api.services.room_service import room_exists

router = APIRouter(tags=["chat"])


async def broadcast_user_list(room_id: str) -> None:
    users = manager.get_users(room_id)
    await manager.broadcast(room_id, {
        "sender": "__user_list__",
        "content": users,
        "timestamp": "",
    })


@router.websocket("/ws/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: str) -> None:
    redis = get_redis()

    if not await room_exists(redis, room_id):
        await websocket.close(code=4004, reason="Room not found or expired")
        return

    # Wait for the join message with the display name
    await websocket.accept()
    try:
        join_data = await websocket.receive_json()
    except WebSocketDisconnect:
        return

    name = join_data.get("sender", "Anonymous")

    # Register with manager (already accepted, so skip accept)
    manager._rooms.setdefault(room_id, {})[websocket] = name

    # Broadcast join notification and updated user list
    await manager.broadcast(room_id, {
        "sender": "__system__",
        "content": f"{name} joined the chat",
        "timestamp": "",
    })
    await broadcast_user_list(room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        disconnect_name = manager.disconnect(room_id, websocket)
        if disconnect_name:
            await manager.broadcast(room_id, {
                "sender": "__system__",
                "content": f"{disconnect_name} left the chat",
                "timestamp": "",
            })
            await broadcast_user_list(room_id)
