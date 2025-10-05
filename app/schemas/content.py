from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentBase(BaseModel):
    title: str
    content: str
    is_public: bool = True


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None


class ContentResponse(ContentBase):
    id: int
    author_id: int
    is_published: bool
    is_moderated: bool
    moderation_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContentModeration(BaseModel):
    status: str  # approved, rejected
    reason: Optional[str] = None
