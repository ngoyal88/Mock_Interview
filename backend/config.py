from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------- LLM / Grok ------------------------------------------------- #
    xai_api_key: str | None = None
    grok_model: str = "grok-beta"
    grok_base_url: str = "https://api.x.ai/v1"
    grok_temp: float = 0.7
    grok_max_tokens: int = 1024

    # ---------- Redis ------------------------------------------------------ #
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # ---------- CORS ------------------------------------------------------- #
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # ---------- Logging ---------------------------------------------------- #
    log_level: str = "INFO"
    log_format: str = "console"           # console | json

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Singleton settings accessor."""
    return Settings()
