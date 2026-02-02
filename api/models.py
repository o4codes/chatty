from datetime import datetime

from pydantic import BaseModel


class RoomCreate(BaseModel):
    pass


class RoomResponse(BaseModel):
    room_id: str
    created_at: datetime
    expires_at: datetime
    ttl_seconds: int


class MessageResponse(BaseModel):
    sender: str
    content: str
    timestamp: datetime


class JoinRoom(BaseModel):
    display_name: str
