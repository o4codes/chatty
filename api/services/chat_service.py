from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_id, []).append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        connections = self._rooms.get(room_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, message: dict) -> None:
        connections = self._rooms.get(room_id, [])
        for connection in connections:
            await connection.send_json(message)

    async def disconnect_room(self, room_id: str) -> None:
        connections = self._rooms.pop(room_id, [])
        for connection in connections:
            try:
                await connection.close(code=4001, reason="Room expired")
            except Exception:
                pass

    def get_room_ids(self) -> list[str]:
        return list(self._rooms.keys())


manager = ConnectionManager()
