from datetime import datetime, timezone, timedelta

from models import Users
from schemas.auth import UserCreate
import uuid
from passlib.context import CryptContext
import string, random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Links
from database import DATABASE_URL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(user_data: UserCreate, db: AsyncSession):
    stmt = select(Users).where(Users.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("User already exists")

    new_user = Users(
        id=uuid.uuid4(),
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_short_link(data, db: AsyncSession) -> str:
    code = data.custom_alias or generate_code()

    # проверка на уникальность
    existing = await db.execute(select(Links).where(Links.short_url == code))
    if existing.scalar_one_or_none():
        raise ValueError("Этот короткий код уже занят")

    exp = datetime.now(timezone.utc) + timedelta(days=14)

    new_link = Links(
        original_url=str(data.original_url),
        short_url=code,
        custom_alias=data.custom_alias,
        create_at=datetime.now(timezone.utc),
        expires_at=exp,
        last_use=datetime.now(timezone.utc),
        click_count=0
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)

    return f"{DATABASE_URL}/{code}"