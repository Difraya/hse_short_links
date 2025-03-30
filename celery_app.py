from celery import Celery
from celery.schedules import crontab
from config import REDIS_BROKER_URL
import multiprocessing
import platform
from sqlalchemy.future import select
from database import get_async_session
from models import Links
from datetime import datetime, timezone

if platform.system() == "Windows":
    multiprocessing.set_start_method("spawn", force=True)

# celery = Celery("tasks", broker="redis://localhost:6379/0")

celery = Celery(
    "celery_app",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BROKER_URL,
    include=["celery_app"]
)

celery.conf.beat_schedule = {
    "delete-expired-links-every-hour": {
        "task": "tasks.delete_expired_links",
        "schedule": crontab(minute=0, hour="*"),  # каждый час
    },
}

@celery.task(name="tasks.delete_expired_links")
def delete_expired_links():
    import asyncio

    async def _delete():
        async with get_async_session() as session:
            result = await session.execute(select(Links))
            links = result.scalars().all()
            for link in links:
                if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
                    await session.delete(link)
            await session.commit()

    asyncio.run(_delete())