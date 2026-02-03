# Chatty

Ephemeral chat rooms that self-destruct after one hour. No accounts, no signup, no data retention.

## Features

- **Instant rooms** — create a chat room and share the link
- **No authentication** — pick a display name and start chatting
- **Real-time messaging** — powered by WebSockets
- **Auto-expiration** — rooms and all messages are deleted after 1 hour
- **Live countdown** — see remaining time before the room expires

## Tech Stack

- **Backend:** FastAPI (Python 3.14)
- **Frontend:** Vue 3 SPA (served by FastAPI)
- **Storage:** Redis (with TTL for automatic expiration)
- **Real-time:** WebSockets

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Redis server running locally (default: `redis://localhost:6379`)

## Getting Started

```bash
# Install dependencies
uv sync

# Start Redis (if not already running)
redis-server

# Run the server
uv run python main.py
```

The server starts at `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

## Project Structure

``` text
api/
├── main.py                # FastAPI app factory and lifespan
├── config.py              # Settings (Redis URL, room TTL, cleanup interval)
├── redis.py               # Redis connection pool
├── models.py              # Pydantic schemas
├── routers/
│   ├── rooms.py           # REST endpoints (POST /api/rooms, GET /api/rooms/{room_id})
│   └── chat.py            # WebSocket endpoint (/ws/{room_id})
├── services/
│   ├── room_service.py    # Room CRUD via Redis
│   └── chat_service.py    # WebSocket connection manager
└── tasks/
    └── cleanup.py         # Background task for disconnecting expired room clients
```

## Configuration

Settings are loaded from environment variables with the `CHATTY_` prefix:

| Variable | Default | Description |
| --- | --- | --- |
| `CHATTY_REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `CHATTY_ROOM_TTL_SECONDS` | `3600` | Room lifetime in seconds |
| `CHATTY_CLEANUP_INTERVAL_SECONDS` | `30` | How often the cleanup task runs |

## API

### REST

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/rooms/` | Create a new room |
| `GET` | `/api/rooms/{room_id}` | Get room info and remaining TTL |

### WebSocket

| Endpoint | Description |
| --- | --- |
| `/ws/{room_id}` | Join a room for real-time messaging |

## License

MIT
