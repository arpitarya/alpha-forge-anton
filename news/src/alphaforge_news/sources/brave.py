"""Brave Search source — free 2k req/month, web search fallback."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from alphaforge_news.base import NewsSource
from alphaforge_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_API_URL = "https://api.search.brave.com/res/v1/web/search"


class BraveSource(NewsSource):
    name = "brave"
    display_name = "Brave Search"
    env_key = "BRAVE_SEARCH_API_KEY"
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
        api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
        if not api_key:
            return []
        india_query = f"{query} India NSE" if "india" not in query.lower() else query
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }
        params = {"q": india_query, "count": str(min(limit, 20)), "country": "in"}
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(_API_URL, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Brave search failed: %s", exc)
            return []

        now = datetime.now(timezone.utc)
        items: list[NewsItem] = []
        for result in data.get("web", {}).get("results", []):
            items.append(NewsItem(
                headline=result.get("title") or "",
                url=result.get("url") or "",
                source_name="Brave Search",
                source_slug=self.name,
                published_at=now,
                summary=(result.get("description") or "")[:300] or None,
            ))
        return items

    async def health(self) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=bool(os.getenv("BRAVE_SEARCH_API_KEY")),
            quota_limit=2000,
            last_error=self._last_error,
        )
