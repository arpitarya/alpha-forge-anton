# News Module — Plan

Standalone, reusable news aggregation module for AlphaForge. Provides real-time Indian
market news from multiple free sources via a single unified interface.

Related plan: [llm/PLAN.md](../../../../llm/PLAN.md)

## Goals

1. Single `NewsService.search()` call aggregates all enabled sources in parallel
2. **Any new news source can be added in one file with no changes elsewhere**
3. **Each source can be tested in complete isolation** — no database, no other modules
4. Fully independent of the LLM module — usable by research agent, screener, alerts, trade
5. All sources are free-tier; API-keyed sources are optional and individually toggleable
6. Deduplication by URL-canonical + title-hash so the same story never appears twice

## Non-goals

- Paid news APIs (Bloomberg, Refinitiv)
- Full-text article scraping (headlines + summaries only)
- Storing news in the database (in-memory cache only, Redis for rate-throttling)

---

## Architecture

```
caller (research agent, screener, dashboard, future: trade signals)
        │
        ▼  await news_service.search(query, symbols, since, limit)
[NewsService]
  ├── SourceRegistry     ← name → NewsSource; auto-populated at import
  ├── fan-out            ← asyncio.gather across all enabled sources
  ├── Deduplicator       ← URL-canonical + title-hash, keeps newest
  ├── Ranker             ← sort by recency; future: relevance score
  └── List[NewsItem]     ← uniform schema returned to caller
        │
        ▼
[NewsSource ABC — each source is one self-contained file]
  ├── RssSource          (Moneycontrol, ET Markets, Mint, BS, Google News)
  ├── YFinanceSource     (per-symbol news via yfinance)
  ├── NseAnnouncementsSource  (corporate filings scraper + daily cache)
  ├── NewsdataSource     (NewsData.io JSON API — free 200 req/day)
  ├── GnewsSource        (gnews JSON API — free 100 req/day)
  ├── TavilySource       (Tavily search API — free 1k/month)
  └── BraveSource        (Brave Search API — free 2k/month)
```

---

## NewsSource Extensibility Contract

The core extensibility design. Every source is a self-contained file implementing
`NewsSource`. The registry is populated at import — no manual wiring needed anywhere else.

### NewsSource ABC

```python
# backend/app/modules/news/news_base.py

class NewsSource(ABC):
    name: str           # unique slug, e.g. "moneycontrol-rss", "newsdata"
    env_key: str | None # env var that enables this source; None = always-on (RSS)
    requires_api_key: bool

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
    # Returns: available=bool, quota_used=int|None, quota_limit=int|None, last_error=str|None
```

### NewsItem schema

```python
# backend/app/modules/news/news_schemas.py

class NewsItem(BaseModel):
    headline: str
    url: str                     # canonical (query-string stripped)
    source_name: str             # e.g. "Moneycontrol", "ET Markets"
    published_at: datetime
    summary: str | None = None
    symbols: list[str] = []      # NSE tickers extracted or provided by source
    image_url: str | None = None
    title_hash: str              # sha256(headline.lower().strip())[:16]
```

### Adding a new source — full checklist

1. Create `backend/app/modules/news/sources/<name>.py`
2. Implement `NewsSource` — self-contained, ≤100 lines
3. Add one line to `sources/__init__.py`:
   ```python
   from .myname import MyNameSource
   REGISTRY["myname"] = MyNameSource
   ```
4. If API-keyed, add `MYNEWS_API_KEY=` to `.env.example`
5. Add standalone tests: `tests/news/test_myname.py`
6. Add a smoke-test section in `backend/notebooks/news_playground.py`

No changes to `NewsService`, `Deduplicator`, routes, or any other source.

### Standalone source testing

Each test file requires only its own API key (or nothing for RSS sources).
No database, no FastAPI app, no other modules needed.

```python
# tests/news/test_newsdata.py

@pytest.mark.asyncio
async def test_keyword_search():
    source = NewsdataSource()
    items = await source.search("Reliance Industries", since=datetime.now() - timedelta(days=7))
    assert len(items) > 0
    assert all(isinstance(i, NewsItem) for i in items)

@pytest.mark.asyncio
async def test_symbol_filter():
    source = NewsdataSource()
    items = await source.search("earnings", symbols=["INFY"])
    assert all("INFY" in i.symbols for i in items)

@pytest.mark.asyncio
async def test_health():
    source = NewsdataSource()
    h = await source.health()
    assert h.available
    assert h.quota_limit == 200   # free tier daily limit
```

Run one source in isolation: `uv run pytest tests/news/test_newsdata.py -v`

---

## Sources Reference

| Source | Type | India coverage | Quota | API key env var | Always-on |
|---|---|---|---|---|---|
| Moneycontrol RSS | RSS XML | Excellent | None | — | Yes |
| ET Markets RSS | RSS XML | Excellent | None | — | Yes |
| Mint / LiveMint RSS | RSS XML | Good | None | — | Yes |
| Business Standard RSS | RSS XML | Good | None | — | Yes |
| Google News query | RSS XML | Broad | None | — | Yes |
| Yahoo Finance (yfinance) | Python lib | Symbol-level | None | — | Yes |
| NSE Announcements | Scraper + daily cache | Corporate filings | None | — | Yes |
| NewsData.io | JSON API | Good | 200 req/day | `NEWSDATA_API_KEY` | No |
| gnews | JSON API | Good | 100 req/day | `GNEWS_API_KEY` | No |
| Tavily Search | JSON API | Broad | 1k req/month | `TAVILY_API_KEY` | No |
| Brave Search | JSON API | Broad | 2k req/month | `BRAVE_SEARCH_API_KEY` | No |

RSS and yfinance sources are always-on (no API key, no quota). API-keyed sources are
skipped gracefully when their env var is absent — the aggregator continues with remaining
sources and does not raise an error.

### NSE Announcements scraper

NSE has no public API for corporate announcements. Strategy:
- Scrape `nseindia.com/companies-listing/corporate-filings/announcements` daily at midnight
- Cache results to Redis with 24h TTL
- Each announcement is a `NewsItem` with `symbols` populated from the company identifier
- Exponential backoff on HTTP errors; source marks itself `available=False` on repeated failure
- Falls back gracefully — if cache is empty and scrape fails, returns empty list (no crash)

---

## Deduplication

Two stories are considered duplicates if either:
- Same URL canonical (scheme + host + path, query-string stripped), OR
- Same `title_hash` (sha256 of headline lowercased and stripped)

When duplicates are detected, the item with the more recent `published_at` is kept.
Deduplication runs after fan-out, before ranking — happens in memory, no persistence.

---

## Notebook Playground

`backend/notebooks/news_playground.py` (Jupytext `.py` ↔ `.ipynb`)

Used during Phase 2 to validate each source before wiring the aggregator.

Covers:
- Call each source directly: `await MoneycontrolRssSource().search("Nifty")`
- Check health of all sources: `await source.health()` for each
- Full aggregator call: `await news_service.search("Reliance", symbols=["RELIANCE"])`
- Dedup verification: run two sources that cover the same story, confirm single result
- Quota tracking: call an API-keyed source multiple times, watch `quota_used` increment
- Timing: measure per-source latency to identify slow sources

---

## API Routes

```
GET  /api/v1/news/search
     ?q=<query>
     &symbols=RELIANCE,INFY       (optional, comma-separated NSE tickers)
     &since=2026-05-09            (optional, ISO date)
     &limit=20                    (default 20, max 50)
     → List[NewsItem]

GET  /api/v1/news/sources
     → List[SourceHealth]         (name, available, quota_used, quota_limit)
```

Both routes are public within the authenticated session (same `Depends(get_current_user)`
as all other routes). No write endpoints — this module is read-only.

---

## Dependency Direction

```
news  →  (nothing in this repo)
```

`news/` is pure Python + HTTP clients. No imports from `llm/`, `research/`, `market/`,
or any other AlphaForge module. Callers import from `news/`, never the reverse.

Allowed consumers: `research/agent_tools.py`, screener signals (future), trade signals
(future), a dashboard news widget (future), price alert rules (future).

---

## File Layout

```
backend/app/modules/news/
├── PLAN.md
├── news_service.py          # NewsService: fan-out, dedup, rank
├── news_base.py             # NewsSource ABC + SourceHealth
├── news_schemas.py          # NewsItem, NewsSearchRequest, NewsSearchResponse
├── news_routes.py           # GET /news/search, GET /news/sources
├── news_dedup.py            # Deduplicator (url-canonical + title-hash)
└── sources/
    ├── __init__.py          # REGISTRY dict + auto-registration on import
    ├── rss.py               # RssSource — all RSS feeds in one file (feed URLs configurable)
    ├── yfinance_news.py     # YFinanceSource
    ├── nse_announcements.py # NseAnnouncementsSource (scraper + Redis cache)
    ├── newsdata.py          # NewsdataSource
    ├── gnews.py             # GnewsSource
    ├── tavily.py            # TavilySource
    └── brave.py             # BraveSource
```

Tests:

```
backend/tests/news/
├── test_news_service.py     # aggregator integration (mocks all sources)
├── test_news_dedup.py       # dedup logic unit tests
└── sources/
    ├── test_rss.py          # standalone — no API key needed
    ├── test_yfinance.py     # standalone — no API key needed
    ├── test_nse.py          # standalone — no API key needed
    ├── test_newsdata.py     # standalone — needs NEWSDATA_API_KEY
    ├── test_gnews.py
    ├── test_tavily.py
    └── test_brave.py
```

---

## Environment Variables (add to `backend/.env.example`)

```
# News Sources — each key enables its source; absent = source skipped gracefully
NEWSDATA_API_KEY=
GNEWS_API_KEY=
TAVILY_API_KEY=
BRAVE_SEARCH_API_KEY=

# Feature flags
NEWS_MAX_RESULTS_PER_SOURCE=15    # cap per-source to avoid one source dominating
NEWS_AGGREGATOR_TIMEOUT_S=8       # max wait before returning partial results
NEWS_NSE_CACHE_TTL_S=86400        # NSE announcements cache TTL (24h)
```

---

## Implementation Phases

| Phase | Deliverable | Notes |
|---|---|---|
| 1 | `news_base.py`, `news_schemas.py`, `NewsItem`, `NewsSource` ABC, `SourceRegistry` | Foundation; no sources yet |
| 2 | Always-on sources: `rss.py`, `yfinance_news.py`, `nse_announcements.py` | Validate each standalone in notebook |
| 3 | `news_dedup.py`, `news_service.py` — aggregator wired with always-on sources | End-to-end smoke test in notebook |
| 4 | API-keyed sources: `newsdata.py`, `gnews.py`, `tavily.py`, `brave.py` | Each validated standalone; add to registry |
| 5 | `news_routes.py` — `GET /news/search`, `GET /news/sources` | Register in `backend/app/modules/__init__.py` |
| 6 | Wire `search_news` tool in `research/agent_tools.py` | Agent can now call the news service |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| NSE scraper gets blocked | Daily cache, exponential backoff, source marks itself unavailable |
| API quota exhausted mid-day | Per-source `SourceHealth.quota_used` tracking; RSS always-on as baseline |
| RSS feeds change structure | Feedparser handles most variations; per-feed field mapping in `rss.py` |
| Slow source delays all results | `NEWS_AGGREGATOR_TIMEOUT_S` returns partial results rather than waiting |
| Duplicate stories dominate | Dedup runs post-fan-out; capped per-source with `NEWS_MAX_RESULTS_PER_SOURCE` |
