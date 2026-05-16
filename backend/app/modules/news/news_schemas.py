"""FastAPI request/response schemas for the news module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NewsSearchRequest(BaseModel):
    q: str = Field(..., description="Search query — company name, topic, or NSE ticker")
    symbols: list[str] = Field(default=[], description="NSE ticker filters e.g. ['RELIANCE']")
    since: datetime | None = Field(None, description="Only return articles after this datetime")
    limit: int = Field(default=20, ge=1, le=50)


class NewsItemResponse(BaseModel):
    headline: str
    url: str
    source_name: str
    source_slug: str
    published_at: datetime
    summary: str | None = None
    symbols: list[str] = []
    image_url: str | None = None
    author: str | None = None
    score: int | None = None


class SourceStatusResponse(BaseModel):
    name: str
    display_name: str
    available: bool
    quota_used: int | None = None
    quota_limit: int | None = None
    last_error: str | None = None
    last_success_at: datetime | None = None
