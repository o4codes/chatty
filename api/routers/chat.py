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

    # Wait for the join message with the display name and avatar
    await websocket.accept()
    try:
        join_data = await websocket.receive_json()
    except WebSocketDisconnect:
        return

    name = join_data.get("sender", "Anonymous")
    avatar = join_data.get("avatar")

    # Register with manager (already accepted, so skip accept)
    user_info = {"name": name, "avatar": avatar}
    manager._rooms.setdefault(room_id, {})[websocket] = user_info

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
            if data.get("type") == "typing":
                await manager.broadcast_except(
                    room_id,
                    {
                        "sender": "__typing__",
                        "content": name,
                        "timestamp": "",
                    },
                    exclude=websocket,
                )
            else:
                # Validate mentions against current room members
                if "mentions" in data and isinstance(data["mentions"], list):
                    current_users = {
                        u["name"] for u in manager.get_users(room_id)
                    }
                    data["mentions"] = [
                        m for m in data["mentions"] if m in current_users
                    ]
                await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        user = manager.disconnect(room_id, websocket)
        if user:
            await manager.broadcast(room_id, {
                "sender": "__system__",
                "content": f"{user['name']} left the chat",
                "timestamp": "",
            })
            await broadcast_user_list(room_id)
