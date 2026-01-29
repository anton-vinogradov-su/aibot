"""Pydantic schemas for API"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# NewsItem schemas
class NewsItemBase(BaseModel):
    title: str = Field(..., max_length=500)
    url: str = Field(..., max_length=1000)
    summary: Optional[str] = None
    source: str = Field(..., max_length=100)
    published_at: datetime
    raw_text: Optional[str] = None


class NewsItemCreate(NewsItemBase):
    pass


class NewsItemResponse(NewsItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Post schemas
class PostBase(BaseModel):
    news_id: int
    generated_text: str
    status: str = "pending"


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Source schemas
class SourceBase(BaseModel):
    type: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    url: str = Field(..., max_length=1000)
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    enabled: Optional[bool] = None
    url: Optional[str] = None


class SourceResponse(SourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Keyword schemas
class KeywordBase(BaseModel):
    word: str = Field(..., max_length=100)


class KeywordCreate(KeywordBase):
    pass


class KeywordResponse(KeywordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Statistics schemas
class StatsResponse(BaseModel):
    total_news: int
    total_posts: int
    published_posts: int
    pending_posts: int
    failed_posts: int
    total_sources: int
    active_sources: int
