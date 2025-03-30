from celery_app import celery
from sqlalchemy.future import select
from database import get_async_session
from models import Links
from datetime import datetime, timezone

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