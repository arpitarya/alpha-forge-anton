# 21 — Web Search Grounding

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Self-hosted SearXNG as primary; DuckDuckGo HTML as fallback | Free |
| **Chosen** | **DuckDuckGo HTML scraping as primary (zero install). Brave Search API free tier (2k/mo) as opt-in second tier if `BRAVE_API_KEY` set. Public SearXNG instance (e.g. `searx.be`) as opt-in third tier if `SEARXNG_URL` set. No reranking in v1 — top-N by source's native ranking. LLM-as-reranker (cheap Groq Llama call) as optional add-on if precision is insufficient.** | Free |

**Why the deviation from the original recommendation**:
- Self-hosted SearXNG via Docker is out (no Docker constraint).
- SearXNG via pip install is possible but adds a long-running Python service to manage on a 16GB MacBook Air; not worth it for the relatively rare `search_web` use case.
- BGE-reranker local model is out (no local models constraint). Drop local reranking; use the LLM as reranker only when needed.
- DuckDuckGo HTML scraping is the most reliable free option that requires zero infrastructure setup.

**Tradeoffs accepted**:
- DuckDuckGo HTML is fragile (HTML changes break parsers; occasional rate limiting). Treat as best-effort.
- No reranking by default means worse top-k relevance for finance-specific queries. Worth measuring before deciding to layer in LLM reranking.
- Public SearXNG instances see your queries — privacy crossover. Document if user opts in.

---

## Context

The news aggregator handles structured Indian financial sources. For long-tail queries ("Has anyone written about the new MUDRA scheme limits?") that don't match curated RSS, the agent needs general web search. SOTA in 2026 means having grounded answers with citations.

Paid options (Tavily, Perplexity API, Brave paid, Bing) are excellent but skipped per the no-paid constraint.

## Options

| Backend | Local/cloud | Auth | Reliability | Index quality |
|---|---|---|---|---|
| **SearXNG** (self-hosted) | Local Docker | None | Excellent (you own it) | Excellent (aggregates 70+ engines) |
| **DuckDuckGo HTML** | Cloud | None | Medium (rate-limited) | Good |
| **DuckDuckGo Instant Answer API** | Cloud | None | Medium | Limited (Wikipedia-style facts) |
| **Brave Search API** | Cloud | Free 2k/mo + paid | Excellent | Very good |
| **Tavily** | Cloud | Free 1k/mo + paid | Excellent | Excellent (LLM-tuned) |
| **Google Programmable Search** | Cloud | API key free + paid | Excellent | Excellent | 100/day free |
| **Kagi** | Cloud | Paid only | Excellent | Excellent |
| **Common Crawl + local index** | Local | None | High setup cost | Variable | Overkill |

## Tradeoffs

- **SearXNG self-hosted** — single Docker container. Aggregates Google, Bing, DuckDuckGo, Yandex, Brave, and dozens more in one query. Returns clean JSON. No rate limits (you're the operator). The setup cost is one `docker run` plus a config file. Best-of-class for the no-paid path.
- **DuckDuckGo HTML scraping** — works without any setup but is fragile (HTML changes break parser; rate limiting from DDG side). Useful as a "works out of the box" fallback before SearXNG is up.
- **Brave free tier** — 2k/mo is plenty for personal use. Trade: ties you to a cloud provider and an API key.
- **Google Programmable Search** — 100 queries/day free with a Google Cloud project. Strong index. Trade: another vendor relationship + setup friction.
- **Tavily** — purpose-built for LLM grounding (returns chunked clean text). Free tier 1k/mo. We previously considered this in [01](01-news-provider.md) for news; same applies here. Keep as opt-in.

## Recommendation

**Three tiers, ordered:**

1. **SearXNG** (primary) — if `SEARXNG_URL` env var is set.
2. **DuckDuckGo HTML** (fallback) — always available, zero-setup.
3. **Brave free** or **Tavily free** (opt-in) — if API key set.

The `search_web` tool tries them in order, returns first successful response.

## Architecture

```mermaid
flowchart TD
    CALL([search_web tool called]) --> T1{SEARXNG_URL\nconfigured?}
    T1 -- yes --> SX[HTTP GET SearXNG\nlocal Docker]
    T1 -- no --> T2
    SX --> RES1{200 OK?}
    RES1 -- yes --> RANK[rerank with BGE-reranker\nlocal; top 5 by relevance]
    RES1 -- no --> T2

    T2{any cloud key\nset?}
    T2 -- yes --> CLOUD[Brave or Tavily]
    T2 -- no --> DDG[DuckDuckGo HTML\nscrape with bs4]

    CLOUD --> RES2{200 OK?}
    RES2 -- yes --> RANK
    RES2 -- no --> DDG

    DDG --> RANK
    RANK --> FORMAT[format as list of\n{title, url, snippet}]
    FORMAT --> RETURN([return to LLM])
```

## SearXNG setup (one-time)

```bash
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -v ./searxng-config:/etc/searxng \
  searxng/searxng:latest
```

Backend config:

```python
# backend/app/core/config.py
SEARXNG_URL: str | None = None  # e.g. "http://localhost:8888"
```

JSON output format is enabled in SearXNG settings (`settings.yml`):

```yaml
search:
  formats:
    - html
    - json
```

Tool calls hit `{SEARXNG_URL}/search?q={query}&format=json`.

## Reranking

Web search results often have weak top-k relevance for finance-specific queries. After fetching, rerank with **BGE-reranker-v2-m3** (local, free, fast). Top 5 reranked results go to the LLM.

Reranker is also useful for the news aggregator results in the future (see [10](10-embedding-model.md) for the broader local-embedding context).

## Result formatting

```
WEB SEARCH RESULTS for "{query}":

[1] {title}
    {url}
    {snippet[:300]}

[2] ...
```

Capped at top 5; total token budget ~2k.

## Privacy

- **SearXNG self-hosted** keeps all queries on your machine (well — SearXNG forwards to upstream engines, but the queries leave from your IP not via a third party that logs).
- **Cloud providers** see every query.
- For sensitive portfolio queries, the user should prefer SearXNG. For general factual questions, any backend is fine.

## When NOT to use web search

The agentic loop should prefer:
1. `search_news` (curated, indexed, fast) for anything news-shaped.
2. `get_price` / `get_fundamentals` for any data query.
3. `search_web` only as a last resort for genuine long-tail web search.

The model's tool descriptions should make this hierarchy explicit so it doesn't reach for web search when news/price tools would answer.

## Open questions

- **SearXNG instance failover** if local Docker is down? Default to DDG fallback; surface a warning in the tool result.
- **Search-result freshness**: SearXNG aggregates real-time but caching layers exist. Pass `time_range=day` for time-sensitive queries.
- **Bot detection**: DDG / Brave / etc. occasionally challenge scraping. SearXNG handles this by rotating; DDG HTML scraping might break sporadically. Tolerate and surface errors.
- **Reranker model size**: BGE-reranker-v2-m3 (~600MB) is fast on CPU. Smaller variants exist (`bge-reranker-base`) at ~280MB for hardware-constrained machines.
- **Adding domain filters**: `search_web(query, prefer_indian=true)` could append `site:moneycontrol.com OR site:livemint.com OR ...` for finance-tuned queries. Useful tool variant.
- **Citation enforcement**: when the model uses web search results, the verifier ([25](25-verifier-pass.md)) should ensure cited URLs actually exist in the tool output, not invented.
