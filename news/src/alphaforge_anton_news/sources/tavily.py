"""Tavily search source — free 1k req/month, general web search fallback."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_API_URL = "https://api.tavily.com/search"


class TavilySource(NewsSource):
    name = "tavily"
    display_name = "Tavily Search"
    env_key = "TAVILY_API_KEY"
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
        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            return []
        # Append India context for relevance
        india_query = f"{query} India NSE BSE" if "india" not in query.lower() else query
        payload = {
            "api_key": api_key,
            "query": india_query,
            "search_depth": "basic",
            "max_results": min(limit, 10),
            "include_answer": False,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(_API_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Tavily search failed: %s", exc)
            return []

        now = datetime.now(timezone.utc)
        items: list[NewsItem] = []
        for result in data.get("results", []):
            items.append(NewsItem(
                headline=result.get("title") or "",
                url=result.get("url") or "",
                source_name="Tavily",
                source_slug=self.name,
                published_at=now,
                summary=(result.get("content") or "")[:300] or None,
            ))
        return items

    async def health(self) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=bool(os.getenv("TAVILY_API_KEY")),
            quota_limit=1000,
            last_error=self._last_error,
        )
