from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from funcs import create_user
from schemas.auth import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        new_user = await create_user(user, db)
        return {"message": "Пользователь создан", "user_id": str(new_user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


