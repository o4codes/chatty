# Chatty

Ephemeral chat rooms that self-destruct after one hour. No accounts, no signup, no data retention.

## Features

- **Instant rooms** — create a chat room and share the link
- **No authentication** — pick a display name and start chatting
- **Avatar selection** — choose from 16 illustrated SVG avatars or use your initial as a fallback
- **Real-time messaging** — powered by WebSockets with auto-reconnect
- **Emoji picker** — built-in picker with 6 categories
- **Online users** — see who's in the room (sidebar on desktop, slide-out panel on mobile)
- **Share link** — copy the room link to clipboard from the chat header
- **Auto-expiration** — rooms and all messages are deleted after 1 hour
- **Live countdown** — see remaining time before the room expires
- **Dark mode** — toggle between light and dark themes

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.14), Uvicorn |
| Frontend | Vue 3, Vue Router 4, Vite 7 |
| Styling | Tailwind CSS 4 |
| Storage | Redis 7 (with TTL for automatic expiration) |
| Real-time | WebSockets |
| Package management | uv (Python), npm (Node) |
| Containerisation | Docker, Docker Compose |

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 22+
- Redis server running locally (default: `redis://localhost:6379`)

## Getting Started

### Local development

```bash
# Install all dependencies (Python + Node)
make install

# Start Redis (if not already running)
redis-server

# Build the frontend and start the server
make serve
```

The server starts at `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

During frontend development you can also run the Vite dev server separately for hot-reload:

```bash
cd frontend && npm run dev   # http://localhost:5173, proxies /api and /ws to :8000
```

### Docker

```bash
docker compose up --build
```

This starts three services:

| Service | Port | Description |
|---------|------|-------------|
| `redis` | 6379 | Redis 7 (exposed to host) |
| `api` | — | FastAPI backend |
| `frontend` | 80 | Nginx serving the Vue SPA, proxying `/api` and `/ws` to the API |

## Makefile

| Target | Description |
|--------|-------------|
| `make install` | Install frontend npm packages and Python dependencies |
| `make build` | Build the Vue SPA to `frontend/dist` |
| `make serve` | Build frontend then start the FastAPI server |
| `make clean` | Remove `frontend/dist` and `frontend/node_modules` |

## Project Structure

```text
chatty/
├── main.py                      # Entry point — mounts SPA static files onto FastAPI
├── Makefile                     # Build automation
├── docker-compose.yml           # Redis + API + Frontend services
├── .env.example                 # Environment variable template
├── pyproject.toml               # Python project metadata & dependencies
├── uv.lock                      # Locked Python dependencies
│
├── api/                         # FastAPI backend
│   ├── main.py                  # App factory, lifespan, router registration
│   ├── config.py                # Settings (Redis URL, room TTL, cleanup interval)
│   ├── redis.py                 # Redis connection pool
│   ├── models.py                # Pydantic request/response schemas
│   ├── Dockerfile               # Python 3.14-slim image with uv
│   ├── routers/
│   │   ├── rooms.py             # REST endpoints (POST /api/rooms, GET /api/rooms/{id})
│   │   └── chat.py              # WebSocket endpoint (/ws/{room_id})
│   ├── services/
│   │   ├── room_service.py      # Room CRUD via Redis
│   │   └── chat_service.py      # WebSocket connection manager
│   └── tasks/
│       └── cleanup.py           # Background task: disconnect clients in expired rooms
│
└── frontend/                    # Vue 3 SPA
    ├── Dockerfile               # Multi-stage build (Node 22 -> Nginx)
    ├── nginx.conf               # Nginx config (SPA routing, API/WS proxy)
    ├── vite.config.js           # Vite config with dev proxies
    ├── package.json             # Node dependencies
    └── src/
        ├── main.js              # Vue app bootstrap
        ├── App.vue              # Root layout component
        ├── style.css            # Global styles & Tailwind imports
        ├── router/
        │   └── index.js         # Routes: / (home), /room/:id (chat)
        ├── views/
        │   ├── HomePage.vue     # Landing page with "Create Room" CTA
        │   └── RoomPage.vue     # Chat room UI
        ├── components/
        │   ├── AppHeader.vue    # Logo and theme toggle
        │   ├── ChatInput.vue    # Message input with emoji picker
        │   ├── ChatMessage.vue  # Message bubble with avatar
        │   ├── CountdownTimer.vue
        │   ├── DisplayNameModal.vue  # Name + avatar selection
        │   └── RoomExpiredOverlay.vue
        ├── composables/
        │   ├── useRoom.js       # Room creation & fetching
        │   ├── useWebSocket.js  # WebSocket with auto-reconnect
        │   ├── useTheme.js      # Dark/light mode
        │   └── useCountdown.js  # Countdown timer logic
        └── data/
            └── avatars.js       # 16 inline SVG avatar illustrations
```

## Configuration

Settings are loaded from environment variables with the `CHATTY_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATTY_REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `CHATTY_ROOM_TTL_SECONDS` | `3600` | Room lifetime in seconds |
| `CHATTY_CLEANUP_INTERVAL_SECONDS` | `30` | How often the cleanup task runs |

## API

### REST

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/rooms/` | Create a new room |
| `GET` | `/api/rooms/{room_id}` | Get room info and remaining TTL |

### WebSocket

Connect to `/ws/{room_id}` for real-time messaging.

**Join handshake** — the first message after connection must be:

```json
{ "sender": "display_name", "avatar": "avatar_id", "type": "join" }
```

**Chat message:**

```json
{ "sender": "display_name", "avatar": "avatar_id", "content": "hello", "timestamp": "ISO8601" }
```

**Server broadcasts:**

| `sender` field | Payload | Purpose |
|----------------|---------|---------|
| `__system__` | `{ "content": "Alice joined the chat" }` | Join/leave notifications |
| `__user_list__` | `{ "content": [{ "name": "Alice", "avatar": "afro" }] }` | Online user list updates |

**Close codes:**

| Code | Meaning |
|------|---------|
| `1000` | Normal close |
| `4001` | Room expired |
| `4004` | Room not found |

Auto-reconnect uses exponential backoff (1s, 2s, 4s) for up to 3 attempts on unexpected disconnects.

## License

MIT
