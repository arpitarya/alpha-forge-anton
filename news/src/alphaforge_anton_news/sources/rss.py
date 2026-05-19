"""RSS source adapter — fetches and parses any feed in rss_feeds.py."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.sources.rss_feeds import RSS_FEEDS
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "AlphaForge Anton/1.0 (Indian market news aggregator)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def _parse_date(entry: feedparser.FeedParserDict) -> datetime:
    raw = entry.get("published") or entry.get("updated") or ""
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


class RssSource(NewsSource):
    category = "rss"
    env_key = None
    requires_api_key = False

    def __init__(self, slug: str, display_name: str, url: str) -> None:
        self.name = slug
        self.display_name = display_name
        self._url = url
        self._last_error: str | None = None

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        try:
            async with httpx.AsyncClient(timeout=6.0, headers=_HEADERS) as client:
                resp = await client.get(self._url)
                resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("RSS %s fetch failed: %s", self.name, exc)
            return []

        q = query.lower()
        items: list[NewsItem] = []
        for entry in feed.entries:
            title: str = entry.get("title", "")
            summary: str = entry.get("summary", "") or entry.get("description", "")
            if q and q not in title.lower() and q not in summary.lower():
                continue
            pub = _parse_date(entry)
            if since and pub < since:
                continue
            items.append(NewsItem(
                headline=title,
                url=entry.get("link", ""),
                source_name=self.display_name,
                source_slug=self.name,
                published_at=pub,
                summary=summary[:300] if summary else None,
            ))
            if len(items) >= limit:
                break
        return items

    async def health(self) -> SourceHealth:
        return self._base_health(available=self._last_error is None, error=self._last_error)


def build_rss_sources() -> list[RssSource]:
    return [RssSource(f["slug"], f["display_name"], f["url"]) for f in RSS_FEEDS]
