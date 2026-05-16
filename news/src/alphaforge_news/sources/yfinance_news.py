"""Yahoo Finance news — per-symbol news via yfinance (optional dep)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from alphaforge_news.base import NewsSource
from alphaforge_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    _YF_AVAILABLE = True
except ImportError:
    _YF_AVAILABLE = False


class YFinanceSource(NewsSource):
    name = "yfinance"
    display_name = "Yahoo Finance"
    env_key = None
    requires_api_key = False
    category = "api"

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        if not _YF_AVAILABLE or not symbols:
            return []
        items: list[NewsItem] = []
        for symbol in symbols:
            # yfinance uses NSE suffix for Indian stocks
            ticker_sym = f"{symbol}.NS" if "." not in symbol else symbol
            try:
                ticker = yf.Ticker(ticker_sym)
                news = ticker.news or []
            except Exception as exc:
                logger.warning("yfinance %s error: %s", ticker_sym, exc)
                continue
            for article in news:
                pub = datetime.fromtimestamp(
                    article.get("providerPublishTime", 0), tz=timezone.utc
                )
                if since and pub < since:
                    continue
                items.append(NewsItem(
                    headline=article.get("title", ""),
                    url=article.get("link", ""),
                    source_name="Yahoo Finance",
                    source_slug=self.name,
                    published_at=pub,
                    symbols=[symbol],
                ))
                if len(items) >= limit:
                    return items
        return items

    async def health(self) -> SourceHealth:
        return self._base_health(available=_YF_AVAILABLE)
