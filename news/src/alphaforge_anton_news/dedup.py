"""Deduplication — URL-canonical + title-hash; keeps the most recent copy."""

from __future__ import annotations

from alphaforge_anton_news.types import NewsItem


def deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    """Return items with duplicates removed, keeping the newest copy of each story."""
    seen_urls: dict[str, NewsItem] = {}
    seen_hashes: dict[str, NewsItem] = {}

    for item in items:
        url_key = item.url.rstrip("/").lower()
        existing_url = seen_urls.get(url_key)
        existing_hash = seen_hashes.get(item.title_hash)

        # If we've seen this URL or hash before, keep whichever is newer
        existing = existing_url or existing_hash
        if existing:
            if item.published_at > existing.published_at:
                seen_urls[url_key] = item
                seen_hashes[item.title_hash] = item
        else:
            seen_urls[url_key] = item
            seen_hashes[item.title_hash] = item

    # Return unique items sorted newest-first
    unique = list({id(v): v for v in seen_urls.values()}.values())
    return sorted(unique, key=lambda i: i.published_at, reverse=True)
