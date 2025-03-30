from celery import Celery
from celery.schedules import crontab
from config import REDIS_BROKER_URL

celery = Celery(
    "tasks",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BROKER_URL,
    include=["tasks"]
)

celery.conf.beat_schedule = {
    "delete-expired-links-every-hour": {
        "task": "tasks.delete_expired_links",
        "schedule": crontab(minute=0, hour="*"),  # каждый час
    },
}