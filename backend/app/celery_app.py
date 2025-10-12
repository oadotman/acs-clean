"""
Celery application configuration for AdCopySurge backend.
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "adcopysurge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Import tasks after celery app creation to avoid circular imports
try:
    from app import tasks
    logger = __import__('logging').getLogger(__name__)
    logger.info("Tasks imported successfully")
except ImportError as e:
    logger = __import__('logging').getLogger(__name__)
    logger.warning(f"Could not import tasks: {e}")

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
    broker_connection_retry_on_startup=True,
)

# Task routes (optional - for task routing)
celery_app.conf.task_routes = {
    "app.tasks.analyze_ad_copy": {"queue": "analysis"},
    "app.tasks.generate_report": {"queue": "reports"},
    "app.tasks.send_email": {"queue": "email"},
}