"""Source registry — auto-populated at import. Each source registers itself here."""

from __future__ import annotations

from alphaforge_news.base import NewsSource
from alphaforge_news.sources.brave import BraveSource
from alphaforge_news.sources.bse_announcements import BseAnnouncementsSource
from alphaforge_news.sources.gnews import GnewsSource
from alphaforge_news.sources.newsdata import NewsdataSource
from alphaforge_news.sources.nse_announcements import NseAnnouncementsSource
from alphaforge_news.sources.reddit import RedditSource
from alphaforge_news.sources.rss import build_rss_sources
from alphaforge_news.sources.tavily import TavilySource
from alphaforge_news.sources.yfinance_news import YFinanceSource

# Ordered by priority: Indian RSS first, then always-on APIs, then social, then web search
def build_all_sources() -> list[NewsSource]:
    sources: list[NewsSource] = []
    sources.extend(build_rss_sources())       # 14 Indian RSS feeds — always-on
    sources.append(NseAnnouncementsSource())  # NSE corporate filings — always-on
    sources.append(BseAnnouncementsSource())  # BSE corporate filings — always-on
    sources.append(YFinanceSource())          # per-symbol — always-on (optional dep)
    sources.append(RedditSource())            # Indian market subreddits — needs key
    sources.append(NewsdataSource())          # newsdata.io — needs key
    sources.append(GnewsSource())             # gnews — needs key
    sources.append(TavilySource())            # web search — needs key
    sources.append(BraveSource())             # web search — needs key
    return sources


__all__ = ["build_all_sources"]
