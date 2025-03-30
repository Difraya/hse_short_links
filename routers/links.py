from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from sqlalchemy import select
from database import get_async_session
from schemas.links import LinkCreate, LinkResponse, LinkUpdate, LinkStats, LinkInfo
from funcs import create_short_link
from models import Links, Users
from managers import fastapi_users
from cache import get_cached_link, set_cached_link, delete_cached_link

current_user = fastapi_users.current_user()

router = APIRouter(prefix="/links", tags=["links"])

@router.post("/shorten", response_model=LinkResponse)
async def shorten_link(
    data: LinkCreate,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        short_url = await create_short_link(data, db)
        return LinkResponse(short_url=short_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{short_code}")
async def delete_link(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user)
):
    result = await db.execute(select(Links).where(Links.short_url == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="URL not found")

    if link.user_id is not None and str(link.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра статистики")

    delete_cached_link(short_code)

    await db.delete(link)
    await db.commit()

    return {"message": f"Link '{short_code}' was deleted"}

@router.put("/{short_code}")
async def update_link(
    short_code: str,
    data: LinkUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user)
):
    result = await db.execute(select(Links).where(Links.short_url == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="URL not found")

    if link.user_id is not None and str(link.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра статистики")

    delete_cached_link(short_code)

    link.original_url = str(data.original_url)
    if data.custom_alias:
        link.short_url = data.custom_alias
        link.custom_alias = data.custom_alias

    link.last_use = datetime.utcnow()

    await db.commit()
    await db.refresh(link)

    return {
        "message": "Link updated",
        "short_url": link.short_url,
        "original_url": link.original_url
    }

@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user)
):
    result = await db.execute(select(Links).where(Links.short_url == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="URL not found")

    if link.user_id is not None and str(link.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра статистики")

    return {
        "original_url": link.original_url,
        "create_at": link.create_at,
        "click_count": link.click_count,
        "last_use": link.last_use
    }

@router.get("/search", response_model=LinkInfo)
async def search_link_by_original_url(
    original_url: str = Query(..., alias="original_url"),
    db: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user),
):
    print("ORIGINAL FROM QUERY:", original_url)
    result = await db.execute(
        select(Links).where(Links.original_url.ilike(original_url))
    )
    link = result.scalar_one_or_none()

    print("RESULT:", link)

    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    if link.user_id is not None and str(link.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return {
        "short_url": link.short_url,
        "original_url": link.original_url,
        "create_at": link.create_at,
    }

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_async_session)
):
    cached_url = get_cached_link(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)

    result = await db.execute(select(Links).where(Links.short_url == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="URL not found")

    if datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(status_code=410, detail="Срок действия ссылки истёк")

    set_cached_link(short_code, link.original_url)

    link.click_count += 1
    link.last_use = datetime.now(timezone.utc)

    await db.commit()

    return RedirectResponse(url=link.original_url)  # http://localhost:8000/links/your_short_url