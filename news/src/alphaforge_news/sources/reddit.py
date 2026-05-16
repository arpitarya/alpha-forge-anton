"""Reddit source — Indian market subreddits via asyncpraw (optional dep)."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from alphaforge_news.base import NewsSource
from alphaforge_news.types import NewsItem, SourceHealth

logger = logging.getLogger(__name__)

try:
    import asyncpraw
    _PRAW_AVAILABLE = True
except ImportError:
    _PRAW_AVAILABLE = False

_SUBREDDITS = [
    "IndiaInvestments",      # best-moderated; high-quality discussion
    "IndianStockMarket",     # NSE/BSE stocks, active
    "DalalStreetTalks",      # market news and tips
    "mutualfunds",           # SIPs, AMC news, fund comparison
    "personalfinanceindia",  # tax, SIP, financial planning context
]
_MIN_SCORE = int(os.getenv("REDDIT_MIN_SCORE", "5"))


class RedditSource(NewsSource):
    name = "reddit-india"
    display_name = "Reddit (Indian Markets)"
    env_key = "REDDIT_CLIENT_ID"
    requires_api_key = True
    category = "social"

    def _client(self) -> "asyncpraw.Reddit":
        return asyncpraw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.getenv("REDDIT_USER_AGENT", "alphaforge:v1"),
        )

    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]:
        if not _PRAW_AVAILABLE or not os.getenv("REDDIT_CLIENT_ID"):
            return []
        search_q = query
        if symbols:
            search_q = f"{query} {' OR '.join(symbols)}"
        items: list[NewsItem] = []
        try:
            async with self._client() as reddit:
                for sub_name in _SUBREDDITS:
                    sub = await reddit.subreddit(sub_name)
                    async for post in sub.search(search_q, limit=5, sort="new"):
                        if post.score < _MIN_SCORE:
                            continue
                        pub = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                        if since and pub < since:
                            continue
                        items.append(NewsItem(
                            headline=post.title,
                            url=f"https://reddit.com{post.permalink}",
                            source_name=f"r/{sub_name}",
                            source_slug=self.name,
                            published_at=pub,
                            summary=post.selftext[:300] if post.selftext else None,
                            author=str(post.author) if post.author else None,
                            score=post.score,
                        ))
                        if len(items) >= limit:
                            return items
        except Exception as exc:
            logger.warning("Reddit search failed: %s", exc)
        return items

    async def health(self) -> SourceHealth:
        available = _PRAW_AVAILABLE and bool(os.getenv("REDDIT_CLIENT_ID"))
        return self._base_health(available=available)
