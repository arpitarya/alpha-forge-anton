"""Indian RSS feed registry — adding a new outlet = one dict entry here, no other changes."""

from __future__ import annotations

# Each entry: slug (unique), display_name, url, category
# category: "markets" | "economy" | "policy" | "general"
RSS_FEEDS: list[dict[str, str]] = [
    # ── Tier 1: Primary Indian market outlets ────────────────────────────────
    {
        "slug": "moneycontrol-rss",
        "display_name": "Moneycontrol",
        "url": "https://www.moneycontrol.com/rss/latestnews.xml",
        "category": "markets",
    },
    {
        "slug": "et-markets-rss",
        "display_name": "ET Markets",
        "url": "https://economictimes.indiatimes.com/markets/rss.cms",
        "category": "markets",
    },
    {
        "slug": "businessline-rss",
        "display_name": "Hindu BusinessLine",
        "url": "https://www.thehindubusinessline.com/markets/?service=rss",
        "category": "markets",
    },
    {
        "slug": "livemint-rss",
        "display_name": "Mint",
        "url": "https://www.livemint.com/rss/markets",
        "category": "markets",
    },
    {
        "slug": "business-standard-rss",
        "display_name": "Business Standard",
        "url": "https://www.business-standard.com/rss/markets-106.rss",
        "category": "markets",
    },
    # ── Tier 2: TV / broadcast business news ─────────────────────────────────
    {
        "slug": "ndtv-profit-rss",
        "display_name": "NDTV Profit",
        "url": "https://www.ndtvprofit.com/feeds/rss",
        "category": "markets",
    },
    {
        "slug": "cnbctv18-rss",
        "display_name": "CNBC TV18",
        "url": "https://www.cnbctv18.com/rss/",
        "category": "markets",
    },
    {
        "slug": "zeebiz-rss",
        "display_name": "Zee Business",
        "url": "https://www.zeebiz.com/rss",
        "category": "markets",
    },
    {
        "slug": "bqprime-rss",
        "display_name": "BQ Prime",
        "url": "https://www.bqprime.com/rss",
        "category": "markets",
    },
    # ── Tier 3: Niche / retail investor focus ─────────────────────────────────
    {
        "slug": "financial-express-rss",
        "display_name": "Financial Express",
        "url": "https://www.financialexpress.com/market/feed/",
        "category": "markets",
    },
    {
        "slug": "moneylife-rss",
        "display_name": "Moneylife",
        "url": "https://www.moneylife.in/rss/",
        "category": "general",
    },
    {
        "slug": "outlook-money-rss",
        "display_name": "Outlook Money",
        "url": "https://www.outlookindia.com/business/feed",
        "category": "general",
    },
    # ── Regulatory (moves markets) ────────────────────────────────────────────
    {
        "slug": "sebi-rss",
        "display_name": "SEBI Announcements",
        "url": "https://www.sebi.gov.in/sebirss.xml",
        "category": "policy",
    },
    {
        "slug": "rbi-rss",
        "display_name": "RBI Notifications",
        "url": "https://www.rbi.org.in/Scripts/RSSFeed.aspx",
        "category": "policy",
    },
]
