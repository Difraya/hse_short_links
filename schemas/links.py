from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
  #  expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    short_url: str

class LinkUpdate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None

class LinkStats(BaseModel):
    original_url: HttpUrl
    create_at: datetime
    click_count: int
    last_use: datetime

class LinkInfo(BaseModel):
    short_url: str
    original_url: HttpUrl
    create_at: datetime