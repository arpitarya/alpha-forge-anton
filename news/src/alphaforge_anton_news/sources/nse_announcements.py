"""NSE corporate announcements — fetches via NSE's public JSON API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_API_URL = "https://www.nseindia.com/api/corporate-announcements?index=equities"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings/announcements",
}
# NSE requires a valid session cookie; we warm it up by visiting the homepage first
_WARMUP_URL = "https://www.nseindia.com"


class NseAnnouncementsSource(NewsSource):
    name = "nse-announcements"
    display_name = "NSE Announcements"
    env_key = None
    requires_api_key = False
    category = "scraper"

    def __init__(self) -> None:
        self._last_error: str | None = None

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        try:
            async with httpx.AsyncClient(timeout=8.0, headers=_HEADERS) as client:
                await client.get(_WARMUP_URL)  # warm up session cookie
                resp = await client.get(_API_URL)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("NSE announcements fetch failed: %s", exc)
            return []

        q = query.lower()
        items: list[NewsItem] = []
        for ann in data if isinstance(data, list) else []:
            subject: str = ann.get("subject") or ann.get("desc") or ""
            symbol: str = ann.get("symbol") or ""
            if symbols and symbol not in symbols:
                continue
            if q and q not in subject.lower() and q not in symbol.lower():
                continue
            pub_raw: str = ann.get("bseDt") or ann.get("an_dt") or ""
            try:
                pub = datetime.fromisoformat(pub_raw).astimezone(timezone.utc)
            except Exception:
                pub = datetime.now(timezone.utc)
            if since and pub < since:
                continue
            url = f"https://www.nseindia.com/companies-listing/corporate-filings/announcements"
            items.append(NewsItem(
                headline=f"[NSE] {symbol}: {subject}",
                url=url,
                source_name="NSE Announcements",
                source_slug=self.name,
                published_at=pub,
                symbols=[symbol] if symbol else [],
            ))
            if len(items) >= limit:
                break
        return items

    async def health(self) -> SourceHealth:
        return self._base_health(available=self._last_error is None, error=self._last_error)
