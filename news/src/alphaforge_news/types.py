"""Shared data types for the news package."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel, model_validator


class NewsItem(BaseModel):
    headline: str
    url: str                      # canonical — query-string stripped
    source_name: str              # human label, e.g. "Moneycontrol"
    source_slug: str              # machine slug, e.g. "moneycontrol-rss"
    published_at: datetime
    summary: str | None = None
    symbols: list[str] = []       # NSE tickers mentioned or tagged by source
    image_url: str | None = None
    author: str | None = None     # populated for Reddit posts
    score: int | None = None      # Reddit upvotes; None for news articles
    title_hash: str = ""

    @model_validator(mode="after")
    def _compute_hash(self) -> NewsItem:
        if not self.title_hash:
            self.title_hash = sha256(
                self.headline.lower().strip().encode()
            ).hexdigest()[:16]
        return self

    @model_validator(mode="after")
    def _canonical_url(self) -> NewsItem:
        """Strip query-string from URL for dedup purposes."""
        if "?" in self.url:
            self.url = self.url.split("?")[0]
        return self


class SourceHealth(BaseModel):
    name: str
    display_name: str
    available: bool
    quota_used: int | None = None
    quota_limit: int | None = None
    last_error: str | None = None
    last_success_at: datetime | None = None
