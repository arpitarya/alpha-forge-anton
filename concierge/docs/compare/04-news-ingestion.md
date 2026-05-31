# 04 — News Ingestion

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | RSS poll on 5-min cadence via APScheduler + Tavily on-demand fallback | Free + Tavily free tier |
| **Chosen** | **Live per-query fan-out via the existing `alphaforge-anton-news` aggregator.** No polling, no scheduler, no `news_articles` DB table. Each concierge turn that needs news calls `aggregator.search()`, which runs all enabled sources in parallel with an 8s per-source timeout, dedupes, and returns ranked `NewsItem[]`. | ₹0 |

**Why the deviation**: the original recommendation assumed we'd build the ingestion ourselves. The existing module already solved this problem with a different (and arguably better-for-this-use-case) pattern — live fan-out per query rather than poll-and-cache. Benefits of reusing it:

- **No DB schema** for news. No `news_articles`, no `news_sources`, no migration, no retention policy.
- **No background scheduler**. APScheduler isn't needed for news ingestion at all.
- **Per-query relevance** is naturally better than "everything from the last 24h" — the aggregator passes the user's query into each source's native search.
- **Source-level isolation**: one source going down doesn't break the rest; per-source timeouts contained by `asyncio.wait_for`.
- **Already battle-tested** — the module is used elsewhere in the app (research agent, screener signals, dashboard widgets).

**Tradeoff accepted**: each news-relevant turn pays the fan-out latency (capped at 8s, typically 1–3s when all sources respond fast). To mitigate, future work can add a short-lived (~5 min) in-memory cache in `news_service` keyed by `(query, symbols)`. Not needed for v1.

---

## Context

Assuming [01](01-news-provider.md) lands on RSS-based ingestion, we need a strategy for *how* news gets pulled into Anton's database. This decision is largely orthogonal to provider choice — even paid APIs need an ingestion pattern.

## Options

### A. Polling (cron-style background fetcher)

A scheduled task hits each source every N minutes, fetches new items, dedupes against the DB, and stores.

### B. RSS native pull

Same as A but specifically uses RSS feed URLs with HTTP conditional requests (`If-Modified-Since`, `ETag`). RSS is itself a polling protocol, so this is a specialization of A.

### C. Webhook push

The provider POSTs new articles to an Anton endpoint as they appear. Requires a publicly reachable URL and provider support.

### D. On-demand pull (lazy)

No background ingest. When the user asks a news question, Claude (via tool-use from [03](03-news-retrieval-pattern.md)) calls a live search API like Tavily or GNews.

## Comparison

| Dimension | A. Polling | B. RSS pull | C. Webhook | D. On-demand |
|---|---|---|---|---|
| Setup cost | Low (one scheduler + handler) | Low (`feedparser` + ETag handling) | High (needs public URL, ngrok/tunnel for local) | Trivial (just the tool) |
| Provider support | Universal | Universal RSS publishers | Rare (mostly Pub/Sub services like Superfeedr, custom enterprise) | Tavily, GNews, Brave |
| Freshness | 1–5 min lag | 1–5 min lag | <30s | Real-time |
| Self-hosted friendly | Yes | Yes | No (needs ingress) | Yes |
| Works offline | Cached corpus stays available | Same | Loses incoming feed | No news available |
| Cost | Free | Free | Subscription to webhook bridge | Per-query API cost |
| Coverage breadth | Whatever's in your fetch loop | All RSS sources you list | Limited to bridge's catalog | Whatever the search API indexes |
| DB grows over time | Yes (needs retention policy) | Yes | Yes | No (ephemeral) |

## Tradeoffs

- **A/B. Polling/RSS** — the workhorse pattern. Anton is self-hosted with no public ingress, so push is awkward. RSS is the established pull format for news and every major Indian financial publisher supports it.
- **C. Webhook** — would be ideal for sub-30-second freshness but requires either a public Anton instance (defeats self-hosted) or a third-party bridge like Superfeedr. Not worth the complexity for a personal portfolio app.
- **D. On-demand only** — eliminates the ingestion problem entirely but creates new ones: no historical corpus to look back at, per-query cost on every news turn, no ability to do background analysis (sentiment, ticker tagging, deduplication).

## Recommendation

**B. RSS pull on a 5-minute schedule, complemented by D. on-demand Tavily lookup as a fallback.**

Implementation shape:
- `news_ingest.py` — `feedparser` against a list of feed URLs, ETag-aware, stores into `news_articles` table.
- Run via FastAPI startup task + APScheduler (already in the stack per [docs/architecture.md](../../docs/architecture.md)) on a 5-minute interval.
- Dedupe by URL canonical form + title hash.
- Tag with tickers via regex against the user's holdings list at ingest time.
- The on-demand fallback (D) gets used only when Claude's `search_news` tool returns zero hits from the local DB — then it transparently falls through to Tavily.

Rationale:
- Self-hosted friendly (no ingress).
- 5-min lag is fine for portfolio context — this isn't a trading bot.
- Building the corpus locally enables future ticker analytics, sentiment trends, etc.
- The fallback path means rare queries don't get "no news available" answers.

## Open questions

- Source list: who's in v1? Probably Mint, ET Markets, MoneyControl, BS, LiveMint, BloombergQuint, RBI press, SEBI press. Add later: company-specific RSS where available.
- Retention: keep 30 days hot, then move to a flat archive? Or just keep indefinitely (small data volume)?
- Should the scheduler be APScheduler in-process or a separate worker process? In-process is simpler; separate is more honest about "long-running" semantics. Given Anton is single-tenant, in-process is fine.
- Per-source rate limiting — do we need it? Most Indian publishers don't rate-limit RSS, but it's polite to send `User-Agent: AlphaForge Anton/0.x (personal use)` and honor 429s.
