"""NewsSource abstract base class — the contract every source must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from alphaforge_anton_news.types import NewsItem, SourceHealth


class NewsSource(ABC):
    name: str           # unique slug — e.g. "moneycontrol-rss", "reddit-india"
    display_name: str   # shown in Preferences UI
    env_key: str | None = None   # env var that enables this source; None = always-on
    requires_api_key: bool = False
    category: str = "api"   # "rss" | "api" | "scraper" | "social"

    @abstractmethod
    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]: ...

    @abstractmethod
    async def health(self) -> SourceHealth: ...

    def _base_health(self, *, available: bool, error: str | None = None) -> SourceHealth:
        return SourceHealth(
            name=self.name,
            display_name=self.display_name,
            available=available,
            last_error=error,
        )
