# 10 — Embedding Model

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Voyage `voyage-finance-2` (or `voyage-3`) | Paid (~$5/yr) |
| **Chosen** | **Not used in v1.** [03](03-news-retrieval-pattern.md) chose in-context injection over RAG, so no embedding model is needed. | ₹0 |

**If RAG is ever revisited under the free-only + no-local-models constraint**: use **Gemini `text-embedding-004` or `gemini-embedding-001`** via the free tier — cloud, zero cost at chat volume, no model weights to manage locally. (The earlier suggestion of local BGE is no longer applicable under the no-local-models rule.) Voyage becomes the option once paid services are acceptable.

---

## Context

**Only relevant if [03](03-news-retrieval-pattern.md) lands on RAG.** Current recommendation is tool-use, so this doc is contingent.

If we do build RAG, we need an embedding model to vectorize news articles. Volume is small: ~200 articles/day × ~5 chunks each = ~1k embedding calls/day for ingest, plus one per chat query. Negligible cost in any scenario.

## Options

| Model | Dim | Cost per MTok | Quality (MTEB) | Domain fit | Hosted/local |
|---|---|---|---|---|---|
| **Voyage voyage-3** | 1024 | $0.06 | Top-tier | General + finance-tuned variants exist | Hosted (Voyage API) |
| **Voyage voyage-3-large** | 1024 | $0.18 | Top-tier+ | Same | Hosted |
| **OpenAI text-embedding-3-small** | 1536 | $0.02 | Very good | General | Hosted (OpenAI API) |
| **OpenAI text-embedding-3-large** | 3072 | $0.13 | Top-tier | General | Hosted |
| **Cohere embed-v3** | 1024 | $0.10 | Top-tier | Multilingual + reranker pairing | Hosted (Cohere API) |
| **BGE-large-en-v1.5** | 1024 | $0 | Strong | General | Local (sentence-transformers) |
| **nomic-embed-text-v1.5** | 768 | $0 | Good | General | Local |
| **Anthropic** | n/a | n/a | n/a | n/a | Anthropic does not offer an embedding endpoint |

## Tradeoffs

- **Voyage** — Anthropic explicitly recommends Voyage as the embedding partner for Claude apps. voyage-3 hits the quality/cost sweet spot. There's also `voyage-finance-2` specifically tuned on financial corpora, which is the obvious pick for news about equities.
- **OpenAI** — cheapest hosted option and very good. The annoyance is bringing in a second API vendor (and key, and billing surface) when Anthropic is already in the stack. But OpenAI embeddings are not a "competitor product" issue — they're commodity.
- **Cohere** — strong, pairs well with their reranker. Adds a third vendor. Probably skip unless reranking becomes important.
- **BGE / Nomic (local)** — free, runs on CPU at low throughput or on GPU fast. Pro: zero per-call cost, fully offline. Con: needs a model file (~500MB), loads into RAM, slower per call (~50ms CPU vs ~30ms hosted). For Anton's volume the runtime cost is invisible — the operational complexity of bundling the model is the real cost.
- **No Anthropic option** — explicitly: Anthropic does not currently sell embeddings. They publicly recommend Voyage.

## Latency

For a single query embedding (the only path where latency hits the user):
- Hosted APIs: 30–80ms.
- Local CPU: 50–200ms depending on model and machine.
- Local GPU: <10ms.

For ingest (batch background): doesn't matter; can run async.

## Cost at our volume

~1k chunks/day × 200 tokens average = 200k tokens/day for ingest. Plus ~50 query embeddings/day at ~50 tokens each = 2.5k tokens/day. Total ~205k tokens/day.

| Model | $/day | $/year |
|---|---|---|
| voyage-3 | $0.012 | ~$4.50 |
| voyage-finance-2 | similar | ~$5 |
| openai 3-small | $0.004 | ~$1.50 |
| openai 3-large | $0.027 | ~$10 |
| BGE local | $0 | $0 |

The cost difference is irrelevant. Decision is on quality, vendor footprint, and operational complexity.

## Recommendation

**Voyage voyage-finance-2 if available in our region; voyage-3 otherwise.**

Rationale:
- Anthropic's own recommended partner — keeps the vendor footprint cohesive (Claude + Voyage instead of Claude + OpenAI).
- Finance-tuned variant materially helps domain retrieval (Indian financial news, ticker context, RBI/SEBI terminology).
- ~$5/year cost is below threshold-for-caring.
- 1024 dims is right-sized for pgvector with HNSW.
- Avoids the "second model vendor" sprawl of mixing Anthropic + OpenAI.

**Fallback**: if Voyage signup or regional access is awkward, **OpenAI text-embedding-3-small** at $1.50/year is fine. Re-embedding the corpus later to switch is a single background job.

**Avoid for v1**: local BGE — saves nothing meaningful and adds model-file management to the deploy.

## Open questions

- Voyage availability from India: their API is hosted in US/EU regions; latency from an Indian deployment of Anton is ~200ms vs ~50ms for a US-hosted instance. Acceptable for ingest, possibly noticeable on query.
- Should we keep the embedding model name + version in a column so a future migration to a higher-dim model is a clean reindex rather than a guess?
- Should query and document use the same model? Voyage offers asymmetric query/document embeddings (input_type parameter) — yes, use them; it's a measurable quality bump.
- Reranking: if RAG precision is insufficient, add Voyage's reranker (`rerank-2`) as a second-stage filter. Defer until measured.
