"""
Application configuration using Pydantic settings.
"""

import os
from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """

    # Basic app settings
    PROJECT_NAME: str = "FastAPI Starter"
    PROJECT_DESCRIPTION: str = "Production-ready FastAPI application template"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "121324354")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # CORS
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                # Try to parse as JSON list
                try:
                    import json

                    return json.loads(v)
                except Exception:
                    pass

            # Split by comma and ensure URLs have protocol
            urls = [url.strip() for url in v.split(",")]
            return [url if "://" in url else f"http://{url}" for url in urls]
        return v

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:5551",
        "http://127.0.0.1:5551",
        "http://127.0.0.1:4551",
        "http://localhost:4551",
        "http://localhost:3000",
        "http://localhost:4500",
        "http://127.0.0.1:4500",
        "https://www.verify.notarizationjustice.sa",
        "file://",
        "null",  # For file:// protocol
    ]

    # Trusted hosts for production
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "*"]

    # Database settings
    PGHOST: str = os.getenv("PGHOST", "localhost")
    PGUSER: str = os.getenv("PGUSER", "postgres")
    PGPASSWORD: str = os.getenv("PGPASSWORD", "Atqan2025")
    PGDATABASE: str = os.getenv("PGDATABASE", "wathq_tenant_services")
    PGPORT: str = os.getenv("PGPORT", "5432")

    DATABASE_URL: PostgresDsn | None = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:Atqan2025@localhost:5432/wathq_tenant_services",
    )

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("PGUSER"),
            password=values.get("PGPASSWORD"),
            host=values.get("PGHOST"),
            port=values.get("PGPORT"),
            path=f"/{values.get('PGDATABASE') or ''}",
        )

    # Redis settings (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Logging
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # Email settings (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    # Testing
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    # First superuser
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")

    # Wathq API
    WATHQ_API_KEY: str = os.getenv("WATHQ_API_KEY", "PnxjlQkR1Rfx3qVoPWWUXJUzaNKxNIj6")

    # Sentry
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    # File uploads
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "uploads")
    AVATARS_DIR: str = os.path.join(UPLOADS_DIR, "avatars")
    MAX_AVATAR_SIZE: int = int(os.getenv("MAX_AVATAR_SIZE", "5242880"))  # 5MB in bytes
    ALLOWED_AVATAR_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]


settings = Settings()
