import json
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "SentinelForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Security & Tokens
    # Default is for dev/testing only; validated on startup
    JWT_SECRET: str = "demo-insecure-secret-key-change-in-production-only-min32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinelforge_dev.db"
    DATABASE_SYNC_URL: str = "sqlite:///./sentinelforge_dev.db"

    # Redis & Queue
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI & OpenAI
    OPENAI_API_KEY: str = "sk-demo-placeholder-not-real-api-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_INVESTIGATION_TIMEOUT_SECONDS: int = 60

    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_EVENTS: str = "100/minute"
    RATE_LIMIT_AI: str = "10/minute"

    # Uploads & Storage
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 10485760  # 10MB

    # CORS Allowed Origins
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "prod")


settings = Settings()
