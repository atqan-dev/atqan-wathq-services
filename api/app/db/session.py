"""
Database session configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

assert settings.DATABASE_URL is not None, "DATABASE_URL is not set"
engine = create_engine(
    str(settings.DATABASE_URL),  # type: ignore
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)