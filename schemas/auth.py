from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from fastapi_users import schemas

class UserCreate(schemas.BaseUserCreate):
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword",
                "username": "your_username"
            }
        }

class UserRead(BaseModel):
    id: UUID
    email: str
    username: str

    class Config:
        from_attributes = True

class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str] = None
    username: Optional[str] = None