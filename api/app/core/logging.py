"""
Logging configuration for the application.
"""

import logging
import sys
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """
    Setup application logging configuration.
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging format - use JSON in production
    if settings.ENVIRONMENT == "production":
        try:
            import pythonjsonlogger.jsonlogger
            log_format = pythonjsonlogger.jsonlogger.JsonFormatter()
        except ImportError:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format if isinstance(log_format, str) else None,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "app.log"),
        ],
    )

    if not isinstance(log_format, str):
        for handler in logging.root.handlers:
            handler.setFormatter(log_format)

    # Set specific loggers
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
