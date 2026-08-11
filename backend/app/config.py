from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path

# Resolve .env relative to this file's directory (backend/app/config.py → backend/.env)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    MONGODB_URI: str  # Required — must be set in backend/.env
    DATABASE_NAME: str = "spendsense_ai"
    FRONTEND_URL: str = "http://localhost:5173"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"
    JWT_SECRET_KEY: str = "spendsense-secret-key-2026-multiuser-security-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = False


settings = Settings()

