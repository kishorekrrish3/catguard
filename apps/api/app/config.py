from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://catguard:catguard_secret@localhost:5432/catguard_db"
    DATABASE_URL_SYNC: str = "postgresql://catguard:catguard_secret@localhost:5432/catguard_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-in-production-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO / S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "catguard_minio"
    MINIO_SECRET_KEY: str = "catguard_minio_secret"
    MINIO_BUCKET: str = "catguard-imagery"
    MINIO_SECURE: bool = False

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    API_PREFIX: str = "/api"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
