"""NewsData.io source — free tier, 200 req/day, strong India coverage."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from alphaforge_news.base import NewsSource
from alphaforge_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_BASE_URL = "https://newsdata.io/api/1/news"


class NewsdataSource(NewsSource):
    name = "newsdata"
    display_name = "NewsData.io"
    env_key = "NEWSDATA_API_KEY"
    requires_api_key = True
    category = "api"

    def __init__(self) -> None:
        self._quota_used: int | None = None
        self._last_error: str | None = None

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        api_key = os.getenv("NEWSDATA_API_KEY", "")
        if not api_key:
            return []
        params: dict[str, str] = {
            "apikey": api_key,
            "q": query,
            "country": "in",
            "language": "en",
            "size": str(min(limit, 10)),
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("NewsData fetch failed: %s", exc)
            return []

        items: list[NewsItem] = []
        for art in data.get("results", []):
            pub_raw: str = art.get("pubDate") or ""
            try:
                pub = datetime.fromisoformat(pub_raw.replace(" ", "T")).astimezone(timezone.utc)
            except Exception:
                pub = datetime.now(timezone.utc)
            if since and pub < since:
                continue
            items.append(NewsItem(
                headline=art.get("title") or "",
                url=art.get("link") or "",
                source_name=art.get("source_id") or "NewsData.io",
                source_slug=self.name,
                published_at=pub,
                summary=(art.get("description") or "")[:300] or None,
                image_url=art.get("image_url"),
            ))
        return items

    async def health(self) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=bool(os.getenv("NEWSDATA_API_KEY")),
            quota_used=self._quota_used,
            quota_limit=200,
            last_error=self._last_error,
        )
