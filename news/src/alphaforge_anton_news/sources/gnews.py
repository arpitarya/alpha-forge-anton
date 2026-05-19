"""gnews source — free tier, 100 req/day, India filter."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_BASE_URL = "https://gnews.io/api/v4/search"


class GnewsSource(NewsSource):
    name = "gnews"
    display_name = "GNews"
    env_key = "GNEWS_API_KEY"
    requires_api_key = True
    category = "api"

    def __init__(self) -> None:
        self._last_error: str | None = None

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        api_key = os.getenv("GNEWS_API_KEY", "")
        if not api_key:
            return []
        params: dict[str, str] = {
            "token": api_key,
            "q": query,
            "country": "in",
            "lang": "en",
            "max": str(min(limit, 10)),
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("GNews fetch failed: %s", exc)
            return []

        items: list[NewsItem] = []
        for art in data.get("articles", []):
            pub_raw: str = art.get("publishedAt") or ""
            try:
                pub = datetime.fromisoformat(pub_raw).astimezone(timezone.utc)
            except Exception:
                pub = datetime.now(timezone.utc)
            if since and pub < since:
                continue
            items.append(NewsItem(
                headline=art.get("title") or "",
                url=art.get("url") or "",
                source_name=art.get("source", {}).get("name") or "GNews",
                source_slug=self.name,
                published_at=pub,
                summary=(art.get("description") or "")[:300] or None,
                image_url=art.get("image"),
            ))
        return items

    async def health(self) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=bool(os.getenv("GNEWS_API_KEY")),
            quota_limit=100,
            last_error=self._last_error,
        )
