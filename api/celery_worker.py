#!/usr/bin/env python3
"""
Celery worker startup script for WATHQ notifications system.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.core.config")

# Import and start Celery
from app.celery_worker.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
