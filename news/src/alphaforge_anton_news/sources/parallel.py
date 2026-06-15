"""Parallel (parallel.ai) search source — paid, opt-in web grounding.

Same `base.py` contract as tavily/brave, but **deliberately not registered in
`build_all_sources`**: Parallel is the explicit paid depth button (handoff §9),
budget-capped in the backend's `grounding_service`, never part of the free
everyday aggregation path. Key from the afbach vault (`PARALLEL_API_KEY`).
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_API_URL = "https://api.parallel.ai/v1beta/search"
_BETA = "search-extract-2025-10-10"


class ParallelSource(NewsSource):
    name = "parallel"
    display_name = "Parallel Search"
    env_key = "PARALLEL_API_KEY"
    requires_api_key = True
    category = "api"

    def __init__(self) -> None:
        self._last_error: str | None = None

    async def search(self, query, symbols=None, since=None, limit=10) -> list[NewsItem]:
        key = os.getenv("PARALLEL_API_KEY", "")
        if not key:
            return []
        q = f"{query} India NSE BSE" if "india" not in query.lower() else query
        headers = {"x-api-key": key, "parallel-beta": _BETA, "Content-Type": "application/json"}
        payload = {
            "objective": q,
            "search_queries": [q],
            "max_results": min(limit, 10),
            "max_chars_per_result": 600,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(_API_URL, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Parallel search failed: %s", exc)
            return []
        now = datetime.now(UTC)
        return [
            NewsItem(
                headline=r.get("title") or "",
                url=r.get("url") or "",
                source_name="Parallel",
                source_slug=self.name,
                published_at=now,
                summary=(" ".join(r.get("excerpts", []))[:300]) or None,
            )
            for r in data.get("results", [])
        ]

    async def health(self) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=bool(os.getenv("PARALLEL_API_KEY")),
            last_error=self._last_error,
        )
