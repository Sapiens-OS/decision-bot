from celery import Celery
from celery.schedules import crontab
from app.core.config import config

# Create Celery app
celery_app = Celery(
    "sapiens_os",
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "check-follow-up-daily": {
        "task": "app.tasks.follow_up.check_follow_up_task",
        "schedule": crontab(hour=10, minute=0),  # Every day at 10:00 UTC
    },
}

# Import tasks
from app.tasks import follow_up
