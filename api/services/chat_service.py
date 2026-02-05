from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[WebSocket, dict]] = {}

    async def connect(self, room_id: str, websocket: WebSocket, user_info: dict) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_id, {})[websocket] = user_info

    def disconnect(self, room_id: str, websocket: WebSocket) -> dict | None:
        connections = self._rooms.get(room_id, {})
        user_info = connections.pop(websocket, None)
        if not connections:
            self._rooms.pop(room_id, None)
        return user_info

    def get_users(self, room_id: str) -> list[dict]:
        return [
            {"name": info["name"], "avatar": info.get("avatar")}
            for info in self._rooms.get(room_id, {}).values()
        ]

    async def broadcast(self, room_id: str, message: dict) -> None:
        connections = self._rooms.get(room_id, {})
        for connection in connections:
            await connection.send_json(message)

    async def broadcast_except(
        self, room_id: str, message: dict, exclude: WebSocket
    ) -> None:
        connections = self._rooms.get(room_id, {})
        for connection in connections:
            if connection is not exclude:
                await connection.send_json(message)

    async def disconnect_room(self, room_id: str) -> None:
        connections = self._rooms.pop(room_id, {})
        for connection in connections:
            try:
                await connection.close(code=4001, reason="Room expired")
            except Exception:
                pass

    def get_room_ids(self) -> list[str]:
        return list(self._rooms.keys())


manager = ConnectionManager()
