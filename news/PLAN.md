# News Module — Plan

Standalone root-level workspace package (`alphaforge-anton-news`). Aggregates Indian market
news and social signals from multiple free sources behind a single unified interface.

Consumed by: research agent, screener signals, trade signals, dashboard widgets, price
alerts — any module that needs news, without depending on the LLM layer.

Related plan: [llm/PLAN.md](../llm/PLAN.md)
Backend facade: [backend/app/modules/news/](../backend/app/modules/news/)

---

## Design priority: Indian markets first

This module is built for trading Indian equities on NSE/BSE. Source selection, coverage,
and defaults all reflect that. International sources are secondary and are only included
when they add India-relevant signal (e.g. US Fed decisions, FII flows).

Primary coverage tier — always-on, no API key:
- NSE and BSE corporate announcements (corporate actions, results, filings)
- SEBI and RBI policy notifications (regulatory events move markets)
- 12 Indian financial news outlets via RSS (Moneycontrol, ET Markets, BusinessLine, etc.)
- Reddit Indian market subreddits (retail sentiment, early signal)
- Yahoo Finance per-symbol news (symbol-level filtering)

Secondary coverage tier — API-keyed, optional:
- NewsData.io, gnews (both support India/NSE symbol filtering)
- Tavily / Brave (web search fallback for obscure queries)

## Goals

1. Single `NewsAggregator.search()` returns deduplicated, ranked results from all sources
2. **Indian market coverage is the default** — every RSS feed is an Indian outlet
3. **Adding a new source is one file, one registry line, zero changes elsewhere**
4. **Adding a new RSS feed is one entry in `rss_feeds.py` — no other code changes**
5. **Every source is testable in complete isolation** — no database, no app, just an API key
6. API keys for all paid/auth sources are viewable and editable from app Preferences
7. Fully independent of `llm/` — importable standalone, zero cross-module imports

## Non-goals

- International news (no Reuters, AP, BBC — not relevant for NSE/BSE trading)
- Full-text article scraping (headlines + summaries only)
- Storing articles in the database (in-memory cache only)
- Paid APIs (Bloomberg, Refinitiv)
- Sentiment scoring (belongs in the LLM/research layer)

---

## Architecture

```
caller (research agent tool, screener, dashboard, trade signals)
        │
        ▼  await aggregator.search(query, symbols, since, limit)
[NewsAggregator]
  ├── SourceRegistry      ← name → NewsSource; auto-populated at import
  ├── asyncio.gather      ← all enabled sources run in parallel
  ├── Deduplicator        ← URL-canonical + title-hash; keeps newest copy
  ├── Ranker              ← sort by recency; relevance scoring in future
  └── List[NewsItem]
```

---

## NewsSource Extensibility Contract

Every source is a self-contained file implementing `NewsSource`. The registry is
populated at import — no changes needed in the aggregator, routes, or any caller.

### NewsSource ABC

```python
# news/src/alphaforge_anton_news/base.py

class NewsSource(ABC):
    name: str             # unique slug — e.g. "moneycontrol-rss", "reddit-india"
    display_name: str     # shown in Preferences UI
    env_key: str | None   # env var that enables this source; None = always-on
    requires_api_key: bool
    category: str         # "rss" | "api" | "scraper" | "social"

    @abstractmethod
    async def search(
        self,
        query: str,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 10,
    ) -> list[NewsItem]: ...

    @abstractmethod
    async def health(self) -> SourceHealth: ...
    # available: bool, quota_used: int|None, quota_limit: int|None, last_error: str|None
```

### NewsItem schema

```python
# news/src/alphaforge_anton_news/types.py

class NewsItem(BaseModel):
    headline: str
    url: str                      # canonical — query-string stripped
    source_name: str              # "Moneycontrol", "r/IndiaInvestments"
    source_slug: str              # matches NewsSource.name
    published_at: datetime
    summary: str | None = None
    symbols: list[str] = []       # NSE tickers mentioned or provided by source
    image_url: str | None = None
    author: str | None = None     # populated for Reddit posts
    score: int | None = None      # Reddit upvotes; None for news articles
    title_hash: str               # sha256(headline.lower().strip())[:16] — for dedup
```

### Adding a new source — complete checklist

1. Create `news/src/alphaforge_anton_news/sources/<name>.py`
2. Implement `NewsSource` — self-contained, ≤100 lines
3. Add one line to `sources/__init__.py`:
   ```python
   from .myname import MyNameSource
   REGISTRY["myname"] = MyNameSource
   ```
4. Add `MYNEWS_API_KEY=` to `backend/.env.example` (if API-keyed)
5. Add `news/tests/sources/test_myname.py`
6. Add a notebook section in `news/notebooks/news_playground.py`

Nothing else changes.

### Adding a new RSS feed — zero Python needed

All RSS outlets share one `RssSource` adapter. Adding a feed is a YAML entry:

```yaml
# news/config/rss_feeds.yaml
feeds:
  - name: my-new-outlet-rss
    display_name: My New Outlet
    url: https://example.com/rss.xml
    category: markets          # general | markets | economy | policy | regional
    always_on: true
```

Re-start the server and the feed is live. No code change, no registry edit.

---

## Sources

### Always-on RSS (no API key, no quota — backbone of the news layer)

One `RssSource` adapter reads `rss_feeds.yaml`. All feeds below are pre-configured.

| Display name | Focus | Category |
|---|---|---|
| Moneycontrol | General markets | markets |
| ET Markets | Markets & economy | markets |
| Mint / LiveMint | Business & markets | markets |
| Business Standard | Markets & corporate | markets |
| Hindu BusinessLine | Business & commodities | markets |
| Financial Express | Markets | markets |
| NDTV Profit | Markets (TV outlet) | markets |
| CNBC TV18 | Markets (TV outlet) | markets |
| Zee Business | Markets (Hindi + English) | markets |
| BQ Prime (BloombergQuint) | In-depth market analysis | markets |
| Moneylife | Retail investor focus | markets |
| Outlook Money | Personal finance & markets | general |
| Google News — Markets | Broad aggregator query | general |
| SEBI Announcements | Regulatory & circular | policy |
| RBI Notifications | Monetary policy & banking | policy |

### Always-on scrapers / libraries (no API key)

| Source | Slug | Notes |
|---|---|---|
| Yahoo Finance news | `yfinance` | Per-symbol via yfinance Python lib |
| NSE Corporate Announcements | `nse-announcements` | Scraper + 24h Redis cache |
| BSE Corporate Announcements | `bse-announcements` | Public JSON API; refreshed every 4h |

### Social — Reddit

| Source | Slug | Subreddits covered |
|---|---|---|
| Reddit Indian Markets | `reddit-india` | r/IndiaInvestments · r/IndianStockMarket · r/DalalStreetTalks · r/mutualfunds · r/personalfinanceindia |

See Reddit section below for credentials and implementation detail.

### API-keyed (optional, free tier — skipped gracefully if key absent)

| Source | Slug | Free quota | Key env var |
|---|---|---|---|
| NewsData.io | `newsdata` | 200 req/day | `NEWSDATA_API_KEY` |
| gnews | `gnews` | 100 req/day | `GNEWS_API_KEY` |
| Tavily Search | `tavily` | 1k req/month | `TAVILY_API_KEY` |
| Brave Search | `brave` | 2k req/month | `BRAVE_SEARCH_API_KEY` |

---

## Reddit Integration

Reddit is the social signal layer — useful for retail sentiment, early discussion of
corporate events, and information not yet in traditional media.

### Credentials

Register a free personal-use app at `reddit.com/prefs/apps`:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT` — e.g. `alphaforge_anton:v1 (by u/your-reddit-username)`

Personal apps: 100 requests/minute free. No payment required.

### Implementation

Library: `asyncpraw` (async Python Reddit API Wrapper).

```python
# news/src/alphaforge_anton_news/sources/reddit.py

class RedditSource(NewsSource):
    name = "reddit-india"
    display_name = "Reddit (Indian Markets)"
    env_key = "REDDIT_CLIENT_ID"
    requires_api_key = True
    category = "social"
    SUBREDDITS = [
        "IndiaInvestments",      # best-moderated; quality long-form discussion
        "IndianStockMarket",     # NSE/BSE stocks; active
        "DalalStreetTalks",      # market talk and news
        "mutualfunds",           # SIPs, fund performance, AMC news
        "personalfinanceindia",  # tax, personal finance context
    ]
    MIN_SCORE = 5                # filter out very low-engagement posts
```

Posts are mapped to `NewsItem`: `headline` = post title, `url` = post permalink,
`summary` = selftext preview (first 300 chars), `score` = upvotes, `author` = u/username.
Symbol extraction: simple regex scan of post title for known NSE ticker patterns.

---

## API Key Management in Preferences

All API-keyed sources are visible and editable from **Preferences → Alpha AI → News Sources**.
No terminal editing of `.env` files needed after initial setup.

### Backend — `NewsSourceSettings` ORM

```python
class NewsSourceSettings(Base):
    source_slug: str        # primary key — "newsdata", "reddit-india", etc.
    encrypted_key: bytes    # Fernet-encrypted (reuses existing FERNET_KEY)
    last_tested_at: datetime | None
    test_status: str        # "ok" | "invalid" | "untested"
    updated_at: datetime
```

Key resolution order:
1. `NewsSourceSettings` table (if row exists)
2. Environment variable fallback
3. Source skipped — aggregator continues without it

Routes:
```
GET    /api/v1/news/settings              → List[SourceKeyStatus]
PUT    /api/v1/news/settings/{slug}       → SourceKeyStatus  # validates before saving
POST   /api/v1/news/settings/{slug}/test  → SourceKeyStatus  # re-validates stored key
DELETE /api/v1/news/settings/{slug}       → 204
```

`PUT` validates the key by calling `source.health()` before persisting — you cannot
accidentally save a broken key.

### Frontend — Preferences → Alpha AI → News Sources

```
ALWAYS ON (no key needed)
[ Moneycontrol RSS ]      ✓ Active — last fetch 4 min ago
[ ET Markets RSS ]        ✓ Active — last fetch 4 min ago
[ Hindu BusinessLine ]    ✓ Active — last fetch 12 min ago
[ NDTV Profit RSS ]       ✓ Active — last fetch 4 min ago
[ CNBC TV18 RSS ]         ✓ Active — last fetch 7 min ago
[ ... 10 more RSS feeds ] ✓ Active
[ NSE Announcements ]     ✓ Active — last sync 2h ago        [Sync now]
[ BSE Announcements ]     ✓ Active — last sync 45 min ago    [Sync now]
[ Yahoo Finance ]         ✓ Active

API-KEYED (optional)
[ Reddit ]    CLIENT_ID set  [Test]  ✓ Working — 98 req/min remaining  [Edit]  [Remove]
              r/IndiaInvestments · r/IndianStockMarket · r/DalalStreetTalks
[ NewsData ]  ••••••••4f2a   [Test]  ✓ Working — 187/200 req remaining [Edit]  [Remove]
[ gnews ]     Not configured                                             [Add key]
[ Tavily ]    ••••••••8c1d   [Test]  ✓ Working — 823/1000 req remaining [Edit]  [Remove]
[ Brave ]     Not configured                                             [Add key]
```

- RSS sources show last-fetch time (polled from Redis cache metadata)
- NSE/BSE show last sync time + "Sync now" button
- API-keyed sources show remaining quota from last `health()` call
- "Test" fires health check inline without navigating away

---

## Deduplication

Two items are duplicates if either:
- Same URL canonical (scheme + host + path, query-string stripped), OR
- Same `title_hash` (sha256 of headline lowercased and stripped)

When duplicates are found, keep the item with the most recent `published_at`.
Dedup runs post-fan-out, in memory, before returning to the caller.

---

## NSE / BSE Implementation Notes

**NSE** — no public API for announcements:
- Scrape `nseindia.com/companies-listing/corporate-filings/announcements`
- Cache to Redis with `NEWS_NSE_CACHE_TTL_S` (default 24h)
- Exponential backoff on failure; marks `available=False` after 3 consecutive failures
- Falls back to empty list on cold cache — never crashes the aggregator

**BSE** — has a public JSON API (no key needed):
- `https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`
- Refreshed every `NEWS_BSE_REFRESH_INTERVAL_S` (default 4h)
- More reliable than NSE scraper; used as supplement

---

## Notebook Playground

`news/notebooks/news_playground.py` (Jupytext `.py` ↔ `.ipynb`)

Used during Phase 2 to validate each source before wiring the aggregator.

- Call each source directly: `await MoneycontrolRssSource().search("Nifty 50")`
- Add a new RSS feed: edit `rss_feeds.yaml`, run notebook cell, confirm it works
- Test Reddit: `await RedditSource().search("TCS results", symbols=["TCS"])`
- Full aggregator: `await aggregator.search("Reliance Industries", symbols=["RELIANCE"])`
- Dedup check: two overlapping sources → single result returned
- Health check all sources: show `quota_used / quota_limit` per source
- Latency timing: identify slow sources to inform timeout setting

---

## Standalone Source Testing

Pattern for each source test file — requires only that source's key:

```python
# news/tests/sources/test_reddit.py

@pytest.mark.asyncio
async def test_keyword_search():
    source = RedditSource()
    items = await source.search("Reliance Q4 results")
    assert len(items) > 0
    assert all(isinstance(i, NewsItem) for i in items)

@pytest.mark.asyncio
async def test_symbol_filter():
    items = await RedditSource().search("earnings", symbols=["INFY"])
    assert all(i.source_slug == "reddit-india" for i in items)

@pytest.mark.asyncio
async def test_min_score_filter():
    items = await RedditSource().search("market open")
    assert all((i.score or 0) >= RedditSource.MIN_SCORE for i in items)

@pytest.mark.asyncio
async def test_health():
    h = await RedditSource().health()
    assert h.available
```

Run one source in isolation: `uv run pytest news/tests/sources/test_reddit.py -v`

---

## File Layout

```
news/                                 ← root-level workspace (like llm/)
├── PLAN.md
├── pyproject.toml                    ← uv workspace member (alphaforge-anton-news)
├── config/
│   └── rss_feeds.yaml                ← data-driven RSS config; adding a feed = YAML entry
├── src/
│   └── alphaforge_anton_news/
│       ├── __init__.py
│       ├── types.py                  # NewsItem, SourceHealth
│       ├── base.py                   # NewsSource ABC
│       ├── aggregator.py             # fan-out + dedup + rank
│       ├── dedup.py                  # URL-canonical + title-hash dedup
│       └── sources/
│           ├── __init__.py           # REGISTRY dict + auto-registration on import
│           ├── rss.py                # RssSource — reads rss_feeds.yaml; one class, all feeds
│           ├── reddit.py             # RedditSource via asyncpraw
│           ├── yfinance_news.py      # YFinanceSource
│           ├── nse_announcements.py  # NseAnnouncementsSource — scraper + Redis cache
│           ├── bse_announcements.py  # BseAnnouncementsSource — public JSON API
│           ├── newsdata.py
│           ├── gnews.py
│           ├── tavily.py
│           └── brave.py
├── notebooks/
│   ├── news_playground.py            # Jupytext source — commit this
│   └── news_playground.ipynb         # generated — gitignored
└── tests/
    ├── test_aggregator.py            # mocks all sources; tests fan-out + dedup
    ├── test_dedup.py
    └── sources/
        ├── test_rss.py               # no key needed; reads rss_feeds.yaml
        ├── test_reddit.py            # needs REDDIT_CLIENT_ID + SECRET
        ├── test_yfinance.py          # no key needed
        ├── test_nse.py               # no key needed
        ├── test_bse.py               # no key needed
        ├── test_newsdata.py          # needs NEWSDATA_API_KEY
        ├── test_gnews.py
        ├── test_tavily.py
        └── test_brave.py
```

Backend thin facade (adds FastAPI + ORM layer on top of `alphaforge_anton_news`):

```
backend/app/modules/news/
├── news_service.py           # wraps NewsAggregator; injects keys resolved from DB
├── news_routes.py            # GET /news/search, GET /news/sources
├── news_schemas.py           # FastAPI request/response models
├── news_settings_service.py  # NewsSourceSettings ORM + key resolution
└── news_settings_routes.py   # GET/PUT/POST/DELETE /news/settings/{slug}
```

Frontend:

```
frontend/src/modules/preferences/
├── NewsSourcesPanel.tsx      # always-on status rows + API-keyed key management rows
└── news-settings.api.ts      # calls /news/settings routes
```

---

## Dependency Direction

```
news/                  →  (nothing in this repo — pure Python + HTTP clients)
backend/modules/news/  →  alphaforge_anton_news   (import from root package)
research/              →  backend/modules/news/  (via search_news agent tool)
```

`news/` is importable standalone with no AlphaForge Anton dependencies.

---

## Environment Variables (add to `backend/.env.example`)

```
# News — API-keyed sources (absent = source skipped gracefully, no error)
NEWSDATA_API_KEY=
GNEWS_API_KEY=
TAVILY_API_KEY=
BRAVE_SEARCH_API_KEY=

# Reddit — all three required to activate the Reddit source
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=alphaforge_anton:v1 (by u/your-reddit-username)

# Aggregator tuning
NEWS_MAX_RESULTS_PER_SOURCE=15      # cap per source so no single source dominates
NEWS_AGGREGATOR_TIMEOUT_S=8         # return partial results rather than waiting longer
NEWS_NSE_CACHE_TTL_S=86400          # NSE announcements cache — 24h
NEWS_BSE_REFRESH_INTERVAL_S=14400   # BSE API refresh cadence — 4h
REDDIT_MIN_SCORE=5                  # filter out posts below this upvote count
```

---

## Implementation Phases

| Phase | Deliverable | Notes |
|---|---|---|
| 1 | `news/` scaffold: `pyproject.toml`, `types.py`, `base.py` ABC, `REGISTRY`, `rss_feeds.yaml` | Foundation; no sources yet |
| 2 | Always-on RSS: `rss.py` reads YAML (15 Indian feeds pre-configured) | Test adding a new feed via YAML only — confirm zero Python needed |
| 3 | Always-on scrapers/libs: `yfinance_news.py`, `nse_announcements.py`, `bse_announcements.py` | Validate each standalone in notebook |
| 4 | `dedup.py` + `aggregator.py` wired with all always-on sources | Smoke test in notebook; confirm dedup across overlapping RSS feeds |
| 5 | `reddit.py` — `RedditSource` via asyncpraw | Standalone test; symbol extraction from post titles |
| 6 | API-keyed sources: `newsdata.py`, `gnews.py`, `tavily.py`, `brave.py` | Each validated standalone; added to registry |
| 7 | Backend facade: `news_service.py`, `news_routes.py`, `news_schemas.py` | Register in `backend/app/modules/__init__.py` |
| 8 | `NewsSourceSettings` ORM + settings routes | Encrypted key storage; key resolution wired |
| 9 | Frontend: `NewsSourcesPanel.tsx` in Preferences → Alpha AI | Status rows, masked keys, Test/Edit/Remove, quota display |
| 10 | Wire `search_news` tool in `research/agent_tools.py` | Research agent can now call the news aggregator |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| NSE scraper gets blocked | Daily Redis cache; exponential backoff; RSS always-on as fallback |
| RSS feed URLs change | One-line fix in `rss_feeds.yaml`; notebook health check detects 404s |
| Reddit API rate limit | asyncpraw handles throttling automatically; `SourceHealth` exposes quota |
| Reddit posts are noisy | `REDDIT_MIN_SCORE` filter; `since` param limits recency |
| Slow source delays results | `NEWS_AGGREGATOR_TIMEOUT_S` returns partial results from fast sources |
| Duplicate stories | Dedup post-fan-out; `NEWS_MAX_RESULTS_PER_SOURCE` prevents one source dominating |
| BSE API schema changes | `test_bse.py` catches it; BSE is more stable than NSE scraper |
