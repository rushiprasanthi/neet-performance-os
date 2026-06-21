"""Celery configuration for background task processing."""

from celery import Celery
from app.config import settings

# Create Celery app using centralized settings
celery_app = Celery(
    "neet",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard kill
    result_expires=3600,      # 1 hour
)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f"Request: {self.request!r}")