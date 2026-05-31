# 01 — News Provider

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | RSS direct + Tavily fallback | Free + Tavily 1k/mo free tier |
| **Chosen** | **Reuse the existing `alphaforge-anton-news` workspace package** ([news/](../../news/)) which already aggregates: 14 Indian RSS feeds + NSE corporate announcements + BSE corporate announcements + SEBI + RBI + Yahoo Finance per-symbol + Reddit (5 Indian subs). Optional API-keyed sources (gnews / newsdata / Tavily / Brave) stay disabled in v1. **Future sources** (Twitter via Nitter, StockTwits, HackerNews, Telegram, YouTube RSS, MCA filings, FRED, …) added per [11-news-source-expansion.md](11-news-source-expansion.md). | ₹0 |

**Why the deviation**: this doc originally compared *external providers* as if we'd build ingestion from scratch. The project already ships a self-contained news aggregator with the exact extensibility model we'd want — pluggable `NewsSource` subclasses, parallel fan-out, dedup. Building anything new would duplicate it. Concierge integrates by calling `get_aggregator().search()` per turn. The "provider choice" therefore becomes **which sources to enable inside the existing aggregator**, which is a different and more flexible question — answered in [11-news-source-expansion.md](11-news-source-expansion.md).

---

## Context

Orff's data source is news. We need a provider that delivers Indian-market-relevant financial news (BSE/NSE tickers, RBI, SEBI, macro), supports keyword + entity search, and has a free or cheap tier suitable for a single-user self-hosted app.

Anton is single-tenant, personal use. Volume is low: maybe 100–500 news fetches/day driven by chat turns + a background refresher. Pricing is per-tenant, not per-user.

## Options

| Provider | Coverage | India financial depth | Free tier | Paid entry | Latency | Notes |
|---|---|---|---|---|---|---|
| **NewsAPI.org** | Global | Shallow (English Indian sources via aggregation) | 100 req/day dev only | $449/mo Business | ~500ms | Dev tier blocks production use |
| **GNews** | Global | Medium (Google News mirror, includes Mint, ET, BS) | 100 req/day | $49/mo Essential (1k/day) | ~700ms | Good India coverage via Google News index |
| **Marketaux** | Financial only | Strong (tagged by ticker, sentiment included) | 100 req/day | $19/mo Bronze (1k/day) | ~600ms | Built for finance, ticker-aware |
| **Polygon.io News** | US-heavy | Weak for India equities | None | Bundled with $29/mo Stocks Starter | ~300ms | India coverage is sparse |
| **Alpha Vantage News & Sentiment** | Global w/ sentiment | Medium | 25 req/day free | $50/mo Premium (75 req/min) | ~800ms | Sentiment scoring built-in |
| **Tavily (Search API)** | Web search, news mode | Strong (live web) | 1k req/mo | $30/mo (4k/mo) | ~1.5s | Designed for LLM grounding; returns clean text |
| **Brave Search API (News)** | Web news index | Medium | 2k req/mo free | $3/CPM | ~600ms | Cheapest at scale, less finance-specific |
| **EOD Historical Data** | Financial | Strong India (NSE/BSE tagged) | None | $19.99/mo News API | ~400ms | Ticker-tagged, but small newsroom set |
| **RSS direct** (Mint, ET Markets, MoneyControl, BS) | Indian financial | Very strong | Free | Free | varies | No search/filter; you build the index |

## Tradeoffs

- **NewsAPI.org** — famous but the dev tier explicitly bars production use, and the $449 jump is absurd for single-tenant. Skip.
- **GNews** — best general-purpose option with real India coverage at $49/mo. Pulls from Google News, so it surfaces Mint, ET, BS, MoneyControl naturally.
- **Marketaux** — purpose-built for finance with sentiment + ticker tagging. $19/mo is the cheapest paid tier with usable volume. Coverage is decent for Indian names but thinner than GNews for general macro.
- **Polygon** — strong if Anton ever adds US equities, but India coverage doesn't justify it.
- **Alpha Vantage** — bundled sentiment is interesting but India ticker tagging is weak.
- **Tavily** — LLM-native (returns clean Markdown chunks ready for context). 1.5s latency is the cost. Pairs well with tool-use pattern (see [03](03-news-retrieval-pattern.md)).
- **Brave** — cheapest but generic; would need post-filtering to get finance signal.
- **EOD Historical** — niche, finance-focused, India-tagged. Worth it if used with the EOD prices API too.
- **RSS direct** — free, deep, and Indian sources publish reliably. Cost is engineering: you build the fetcher, deduper, and search index. For a single-tenant personal app, that engineering cost is small and one-time.

## Recommendation

**RSS direct from a curated source list + Tavily as an on-demand fallback for queries the RSS index can't answer.**

Rationale:
- **Cost**: $0 for the bulk of traffic; Tavily's free 1k/mo handles tail queries.
- **Coverage**: Indian financial RSS is excellent — Mint, ET Markets, MoneyControl, BS, Bloomberg Quint, LiveMint Markets, RBI press releases, SEBI orders.
- **Latency**: RSS is pre-indexed locally; queries are DB-fast.
- **Control**: Owning the index means we can dedupe, tag by ticker via simple regex against the user's holdings, and store the corpus for embedding (relevant if RAG wins in [03](03-news-retrieval-pattern.md)).
- **Tradeoff accepted**: build a small RSS poller + storage table. Maps to ~150 LOC across `news_ingest.py`, `news_models.py`, `news_service.py`.

**Fallback path** if RSS proves too noisy: switch to **GNews paid ($49/mo)** which gives the same sources via API with built-in dedup.

## Open questions

- Do we want a sentiment column at ingest time, or compute it lazily via Haiku on demand?
- Should RBI/SEBI primary sources (official RSS) be a separate tier with higher trust weight?
- What's the retention policy — keep 30 days hot in Postgres and archive older to a flat file?
