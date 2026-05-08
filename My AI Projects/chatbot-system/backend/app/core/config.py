from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
