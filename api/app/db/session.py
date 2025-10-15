"""
Database session configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Handle both sync and async database URLs
database_url = str(settings.DATABASE_URL)
if database_url.startswith("postgresql+asyncpg://"):
    # Convert async URL to sync URL
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)