"""
NaviAid Configuration – Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://naviaid:naviaid_secret@localhost:5432/naviaid"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "super-secret-change-me-in-production-64chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Admin
    ADMIN_EMAIL: str = "admin@naviaid.in"
    ADMIN_PASSWORD: str = "Admin@NaviAid2024"

    # External APIs – Jobs & Schemes
    RAPIDAPI_KEY: str = ""          # JSearch (RapidAPI) – free 200 req/month
    ADZUNA_APP_ID: str = ""         # Adzuna – free 250 req/month
    ADZUNA_APP_KEY: str = ""        # Adzuna app key

    # ML
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_URL: str = "http://localhost:11434"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
