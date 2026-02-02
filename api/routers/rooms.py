from fastapi import APIRouter, HTTPException

from api.models import RoomCreate, RoomResponse
from api.redis import get_redis
from api.services.room_service import create_room, get_room

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=201)
async def create_room_endpoint(body: RoomCreate) -> RoomResponse:
    redis = get_redis()
    room = await create_room(redis)
    return room


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room_endpoint(room_id: str) -> RoomResponse:
    redis = get_redis()
    room = await get_room(redis, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found or expired")
    return room
