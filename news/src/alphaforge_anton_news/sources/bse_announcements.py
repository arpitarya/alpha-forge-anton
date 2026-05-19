"""BSE corporate announcements — uses BSE's public JSON API (no auth required)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from alphaforge_anton_news.base import NewsSource
from alphaforge_anton_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

_API_URL = (
    "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    "?strCat=-1&strPrevDate=&strScrip=&strSearch=P&strToDate=&strType=C&subcategory=-1"
)
_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bseindia.com",
    "Origin": "https://www.bseindia.com",
}


class BseAnnouncementsSource(NewsSource):
    name = "bse-announcements"
    display_name = "BSE Announcements"
    env_key = None
    requires_api_key = False
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
        try:
            async with httpx.AsyncClient(timeout=8.0, headers=_HEADERS) as client:
                resp = await client.get(_API_URL)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("BSE announcements fetch failed: %s", exc)
            return []

        table: list[dict] = data.get("Table", []) if isinstance(data, dict) else []
        q = query.lower()
        items: list[NewsItem] = []
        for row in table:
            subject: str = row.get("NEWSSUB") or row.get("HEADLINE") or ""
            ticker: str = row.get("SCRIP_CD") or row.get("NSE_SYMBOL") or ""
            if symbols and ticker not in symbols:
                continue
            if q and q not in subject.lower() and q not in ticker.lower():
                continue
            pub_raw: str = row.get("NEWS_DT") or row.get("DissemDT") or ""
            try:
                pub = datetime.fromisoformat(pub_raw.replace("T", " ")).astimezone(timezone.utc)
            except Exception:
                pub = datetime.now(timezone.utc)
            if since and pub < since:
                continue
            news_id: str = row.get("NEWSID") or ""
            url = f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{news_id}.pdf"
            items.append(NewsItem(
                headline=f"[BSE] {ticker}: {subject}",
                url=url if news_id else "https://www.bseindia.com/corporates/ann.html",
                source_name="BSE Announcements",
                source_slug=self.name,
                published_at=pub,
                symbols=[ticker] if ticker else [],
            ))
            if len(items) >= limit:
                break
        return items

    async def health(self) -> SourceHealth:
        return self._base_health(available=self._last_error is None, error=self._last_error)
