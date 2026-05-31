# 11 — News Source Expansion (Free Sources Backlog)

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Add high-value free sources behind the existing `NewsSource` ABC, prioritized by signal quality | ₹0 |
| **Chosen** | **Same — extend the existing `alphaforge-anton-news` package one source-file at a time.** Each new source is a one-file `NewsSource` subclass dropped into [news/src/alphaforge_anton_news/sources/](../../news/src/alphaforge_anton_news/sources/) and registered in `sources/__init__.py`. No changes elsewhere. Order of addition driven by the priority table below. | ₹0 |

---

## Context

The user wants free-tier news fetching to include social signals (Twitter, Reddit, etc.) and to be designed so **any** new free source can be added cheaply. The good news: the existing news module is already built for this. This doc:

1. Reaffirms the extensibility contract — adding a source is one file, no other changes.
2. Catalogs candidate free sources with realistic notes on each (rate limits, ToS, reliability).
3. Recommends a prioritized addition order.

---

## Extensibility Contract (already in place)

`alphaforge-anton-news` defines a `NewsSource` ABC ([news/src/alphaforge_anton_news/base.py](../../news/src/alphaforge_anton_news/base.py)):

```python
class NewsSource(ABC):
    name: str                     # unique slug
    display_name: str             # UI label
    env_key: str | None = None    # env var; None = always-on
    requires_api_key: bool = False
    category: str = "api"

    @abstractmethod
    async def search(self, query, symbols=None, since=None, limit=10) -> list[NewsItem]: ...

    @abstractmethod
    async def health(self) -> SourceHealth: ...
```

Every source maps its native API to a uniform `NewsItem` shape (headline / url / source_name / published_at / summary / symbols / author / score). The aggregator fans them all out in parallel, dedupes by canonical URL + title hash, and returns a unified list.

**Adding a source requires three lines of work**:

1. New file `sources/<slug>.py` implementing `NewsSource`.
2. One import + one append in `sources/__init__.py:build_all_sources()`.
3. (Only if `requires_api_key=True`) — set the env var documented in the source.

**Zero changes** in concierge, routes, schemas, types, dedup, or any caller.

---

## Currently Included (no work needed)

| Source | Slug | Category | Auth | Status |
|---|---|---|---|---|
| Mint / ET Markets / MoneyControl / BS / NDTV Profit / CNBC TV18 / Zee Business / BQ Prime / Financial Express / Moneylife / Outlook Money / Hindu BusinessLine | (14 slugs) | rss | None | Always-on |
| SEBI announcements | `sebi-rss` | regulatory | None | Always-on |
| RBI notifications | `rbi-rss` | regulatory | None | Always-on |
| NSE corporate announcements | `nse-announcements` | regulatory | None | Always-on |
| BSE corporate announcements | `bse-announcements` | regulatory | None | Always-on |
| Yahoo Finance per-symbol | `yfinance-news` | api | None | Always-on |
| Reddit (Indian markets) | `reddit-india` | social | API key | Opt-in (`REDDIT_CLIENT_ID`) |
| NewsData.io | `newsdata` | api | API key | Opt-in |
| GNews | `gnews` | api | API key | Opt-in |
| Tavily | `tavily` | api | API key | Opt-in |
| Brave Search News | `brave` | api | API key | Opt-in |

---

## Proposed Additions — Prioritized Free Sources

### Tier 1: High signal, fully free, low friction

| Source | Slug (proposed) | What it adds | Auth reality | Notes |
|---|---|---|---|---|
| **StockTwits** | `stocktwits` | Real-time Twitter-style chatter scoped to tickers; sentiment-tagged | Free public REST API, no key | `GET https://api.stocktwits.com/api/2/streams/symbol/{TICKER}.json`. Limit ~200 req/hr unauth. The realistic "Twitter for stocks" replacement. **Strong pick.** |
| **HackerNews** | `hackernews-algolia` | Tech, macro, IPO, US policy signal that often precedes Indian-market reactions | Free Algolia search API, no key | `https://hn.algolia.com/api/v1/search?query={q}&tags=story`. Unlimited. |
| **Google News (RSS-by-query)** | `google-news-rss` | Long-tail recall — finds articles other RSS misses | Free, no key | `https://news.google.com/rss/search?q={q}+when:1d&hl=en-IN&gl=IN`. Beware deduping vs other Indian feeds. |
| **YouTube channel RSS** (Indian finance creators) | `youtube-finance-rss` | Video commentary by P.R. Sundar, CA Rachana, Pranjal Kamra, etc. | Free, no key | Per-channel `https://www.youtube.com/feeds/videos.xml?channel_id={id}`. Curate channel list like `rss_feeds.py`. |
| **MCA (Ministry of Corporate Affairs) filings** | `mca-filings` | Director changes, charge filings, board resolutions — leading indicator for corporate events | Free MCA21 portal | No official API; scrape filings RSS or daily filings page. |
| **Telegram public channels** (Indian market) | `telegram-public` | Real-time alerts from "MarketScreener", "Stock Insiders", popular Indian channels | Free Telegram API (telethon needs API ID + hash, both free from my.telegram.org) | Risk: ToS strict on automated reads; use sparingly. |

### Tier 2: Useful but lower priority or with reliability caveats

| Source | Slug (proposed) | What it adds | Auth reality | Notes |
|---|---|---|---|---|
| **X / Twitter via Nitter RSS** | `nitter-rss` | Twitter signal without the broken X API | Free, no key | Use a self-hosted Nitter instance or rotate public ones. **Caveat**: X has blocked Nitter scrapers repeatedly through 2024–2025; reliability is poor. Treat as best-effort. |
| **Bluesky** | `bluesky` | Growing finance community after Twitter exodus | Free AT Protocol public read | `GET https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q={q}`. Indian finance community is still small but growing. |
| **Mastodon (financial instances)** | `mastodon-fin` | Long-form finance posts | Free, no key for public timeline | `https://{instance}/api/v1/timelines/tag/{tag}`. Use econtwitter.net or similar. |
| **TradingView ideas** | `tradingview-ideas` | Chart-based trade ideas | Free public read, no key | `https://www.tradingview.com/symbols/{ticker}/ideas/` — scrape or use public JSON endpoints. |
| **Reuters India RSS** | `reuters-india-rss` | Wire-service quality coverage | Free RSS, no key | `https://www.reutersagency.com/feed/?best-topics=business&post_type=best` (URL evolves). |
| **CoinGecko News** | `coingecko-news` | Crypto context for diversified portfolios | Free public API, key optional | `GET https://api.coingecko.com/api/v3/news`. |
| **CoinDesk RSS** | `coindesk-rss` | Crypto market news | Free RSS, no key | Standard RSS. |

### Tier 3: Foreign / macroeconomic — FII-flow context

| Source | Slug (proposed) | What it adds | Auth reality | Notes |
|---|---|---|---|---|
| **FRED (US Fed economic data)** | `fred-releases` | FOMC announcements, rates, inflation — drives FII flows | Free API, key from research.stlouisfed.org | Curate ~20 high-impact series IDs. |
| **US Fed RSS** | `fed-rss` | FOMC statements, press releases | Free RSS, no key | `https://www.federalreserve.gov/feeds/press_all.xml`. |
| **ECB RSS** | `ecb-rss` | EU monetary policy | Free RSS, no key | Affects global risk-on/risk-off. |
| **Financial Times Markets RSS** | `ft-markets-rss` | Limited free RSS headlines | Free RSS (truncated articles, no key) | Use for headline scan only; bodies require subscription. |

### Tier 4: Indian regulators beyond SEBI/RBI

| Source | Slug (proposed) | What it adds | Auth reality | Notes |
|---|---|---|---|---|
| **IRDAI** (insurance regulator) | `irdai-rss` | Insurance sector news (HDFC Life, SBI Life, etc.) | Free, no key | Standard RSS from irdai.gov.in. |
| **PFRDA** (pension regulator) | `pfrda-rss` | NPS / pension fund news | Free, no key | Standard RSS. |
| **CCI** (Competition Commission) | `cci-rss` | M&A approvals / blocks | Free, no key | Material for large-cap M&A. |
| **MOSPI** (statistics ministry) | `mospi-rss` | GDP, IIP, CPI releases | Free, no key | Macro release calendar. |
| **Income Tax / GST council** | `gst-council-rss` | Tax rate changes affecting sector profitability | Free, no key | Less reliable RSS; may need scraper. |

---

## Recommendation

**Add in priority order** (Tier 1 first), one source per PR. Each is a self-contained file plus a one-line registry edit:

1. `stocktwits` — biggest immediate win. Direct Twitter-style sentiment for stocks. Free, reliable, no auth.
2. `hackernews-algolia` — free, unlimited, covers tech / macro / IPO chatter.
3. `google-news-rss` — long-tail recall; catches what curated RSS misses.
4. `youtube-finance-rss` — Indian-finance YouTuber commentary, often early on themes.
5. `mca-filings` — director / charge / board filings (leading indicator).
6. `nitter-rss` *(if a stable Nitter instance is reachable)* — Twitter best-effort.
7. `telegram-public` — high signal but ToS-risky; sparingly.
8. Tier 2/3/4 as needed based on observed user queries.

**Defer / never**: official X/Twitter API (post-Musk free tier is unusable for reading), paid APIs (Bloomberg / Refinitiv — per project non-goals), scraping anti-bot–protected sites (high maintenance, breaks frequently).

---

## Why this design scales

The existing aggregator + ABC pattern means **the marginal cost of a new source is the source's own complexity, nothing else**. Aggregator code doesn't change. Concierge doesn't change. The dedup logic doesn't change. The frontend doesn't change.

What does scale work look like? For a typical Tier 1 source like StockTwits:

```
news/src/alphaforge_anton_news/sources/stocktwits.py    ← ~70 LOC
news/src/alphaforge_anton_news/sources/__init__.py      ← +2 lines
news/tests/test_stocktwits.py                            ← ~40 LOC
```

That's it. Ship one source at a time, each landable in under an hour.

---

## Open questions

- **Per-user source toggles** — should each user pick which sources are enabled, or is the global env-var model sufficient for a single-tenant personal app? Single-tenant says env vars are fine; add per-user only if Anton goes multi-user.
- **Per-source weight in ranking** — right now dedup happens but ranking is just by recency. Should some sources (SEBI, NSE official) be weighted higher than chatter sources (Reddit, StockTwits) before passing to the LLM? Probably yes — add a `priority: int` field to `NewsSource` and use it in `aggregator.search()`.
- **In-memory query cache** — repeated identical queries within 5 minutes (likely in multi-turn chats) currently re-run the fan-out. A `cachetools.TTLCache` keyed by `(query, sorted symbols)` would help; add when latency becomes a complaint.
- **Source-level rate limiting** — for sources without official limits (e.g., RSS feeds), be polite: send `User-Agent: AlphaForge Anton/0.x (personal use)` and respect HTTP 429.
- **Nitter instance rotation** — if `nitter-rss` is added, build in instance failover from a list, because individual instances die regularly.
