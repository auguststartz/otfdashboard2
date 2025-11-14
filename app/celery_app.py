"""
Celery Application Configuration for Background Tasks
"""
from celery import Celery
from app.config import Config

# Create Celery instance
celery = Celery(
    'rightfax_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Import tasks to register them
from app.tasks import submission_tasks, xml_tasks

# Make Celery instance available
__all__ = ['celery']
