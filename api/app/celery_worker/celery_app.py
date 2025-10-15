"""
Celery configuration for WATHQ application.
"""

import os
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "wathq_app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.celery_worker.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Beat settings for periodic tasks
    beat_schedule={
        "cleanup-expired-notifications": {
            "task": "app.celery_worker.tasks.cleanup_expired_notifications",
            "schedule": 3600.0,  # Every hour
        },
        "send-pending-notifications": {
            "task": "app.celery_worker.tasks.send_pending_notifications",
            "schedule": 60.0,  # Every minute
        },
    },

    # Task routing
    task_routes={
        "app.celery_worker.tasks.*": {"queue": "wathq_queue"},
    },
)

if __name__ == "__main__":
    celery_app.start()
