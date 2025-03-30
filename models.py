from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass


class Users(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(PG_TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))

class Links(Base):
    __tablename__ = "link"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    original_url = Column(String, nullable=False)
    short_url = Column(String, nullable=False)
    custom_alias = Column(String, nullable=True)
    create_at = Column(PG_TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    expires_at = Column(PG_TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    last_use = Column(PG_TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    click_count = Column(Integer, nullable=False)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=True)

    user = relationship("Users", backref="links")


#В alembic/env.py нужно добавить:

#from myapp.models import Base  # путь к твоему Base
#target_metadata = Base.metadata
#В alembic.ini:
#sqlalchemy.url = postgresql+psycopg://postgres:yourpassword@localhost:5432/shortlinks