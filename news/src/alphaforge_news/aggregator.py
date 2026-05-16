"""NewsAggregator — fans out to all enabled sources in parallel, deduplicates."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime

from alphaforge_news.base import NewsSource
from alphaforge_news.dedup import deduplicate
from alphaforge_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_TIMEOUT_S = float(os.getenv("NEWS_AGGREGATOR_TIMEOUT_S", "8"))
_MAX_PER_SOURCE = int(os.getenv("NEWS_MAX_RESULTS_PER_SOURCE", "15"))


class NewsAggregator:
    def __init__(self, sources: list[NewsSource]) -> None:
        self._sources = sources

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 20,
    ) -> list[NewsItem]:
        tasks = [
            self._fetch(src, query, symbols, since)
            for src in self._sources
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        all_items: list[NewsItem] = []
        for batch in results:
            all_items.extend(batch)
        return deduplicate(all_items)[:limit]

    async def _fetch(
        self,
        source: NewsSource,
        query: str,
        symbols: list[str] | None,
        since: datetime | None,
    ) -> list[NewsItem]:
        try:
            items = await asyncio.wait_for(
                source.search(query, symbols=symbols, since=since, limit=_MAX_PER_SOURCE),
                timeout=_TIMEOUT_S,
            )
            return items
        except TimeoutError:
            logger.warning("Source %s timed out after %ss", source.name, _TIMEOUT_S)
        except Exception as exc:
            logger.warning("Source %s error: %s", source.name, exc)
        return []

    async def health(self) -> list[SourceHealth]:
        tasks = [src.health() for src in self._sources]
        return list(await asyncio.gather(*tasks, return_exceptions=False))
