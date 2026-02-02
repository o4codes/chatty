from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    ROOM_TTL_SECONDS: int = 3600
    CLEANUP_INTERVAL_SECONDS: int = 30

    model_config = {"env_prefix": "CHATTY_"}


settings = Settings()
