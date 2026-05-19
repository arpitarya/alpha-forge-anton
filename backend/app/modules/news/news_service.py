"""NewsService — singleton wrapper around NewsAggregator for backend use."""

from __future__ import annotations

from alphaforge_anton_news import NewsAggregator
from alphaforge_anton_news.sources import build_all_sources


def _build() -> NewsAggregator:
    return NewsAggregator(sources=build_all_sources())


# Module-level singleton — initialised once on first import
_aggregator: NewsAggregator | None = None


def get_aggregator() -> NewsAggregator:
    global _aggregator
    if _aggregator is None:
        _aggregator = _build()
    return _aggregator
