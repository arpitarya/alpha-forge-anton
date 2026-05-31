# 09 — Vector DB

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | pgvector (only if RAG wins in [03](03-news-retrieval-pattern.md)) | Free |
| **Chosen** | **Not used in v1.** [03](03-news-retrieval-pattern.md) chose in-context injection over RAG, so no vector store is needed. This doc stays as reference for when RAG is reconsidered. | ₹0 |

**If RAG is ever revisited**: the recommendation (pgvector) still holds — it's free and already runs in our Postgres.

---

## Context

**Only relevant if [03](03-news-retrieval-pattern.md) lands on RAG.** Current recommendation is tool-use, so this doc is contingent on a future RAG decision.

If we do build RAG over the news corpus, we need a vector store for embeddings. Scale is small: ~30 days × ~200 articles/day × maybe ~5 chunks each = ~30k vectors. At 1024-dim float32 that's ~120MB total.

## Options

| Store | Hosted/local | Index type | Hybrid search | Already in stack | Setup cost |
|---|---|---|---|---|---|
| **pgvector** | Local (Postgres ext) | IVFFlat, HNSW | Native via tsvector + cosine | Yes (just enable extension) | Trivial |
| **Qdrant** | Local Docker or hosted | HNSW | Yes (BM25 + dense) | No | Medium (new service) |
| **Chroma** | Local (sqlite/duckdb) | HNSW | Limited | No | Low |
| **Weaviate** | Local Docker or hosted | HNSW | Yes (BM25 hybrid native) | No | Medium |
| **Pinecone** | Hosted only | Proprietary | Yes (sparse-dense) | No | Low (API key); ongoing $ |
| **LanceDB** | Local (file-based) | IVF-PQ | Limited | No | Low |

## Tradeoffs at our scale

At 30k vectors, *every* option is fast enough — sub-10ms top-k retrieval. Index type, recall benchmarks, and HNSW vs IVFFlat distinctions are essentially noise at this scale. The decision collapses to ops surface and integration cost.

- **pgvector** — zero new services, one Alembic migration to `CREATE EXTENSION vector`, one new table with a `vector(1024)` column and an HNSW index. Hybrid search (combine BM25 keyword score with cosine similarity) is a single SQL query.
- **Qdrant** — best dedicated vector DB by most benchmarks, but adding a Docker container for 30k vectors is silly. Reconsider if the corpus grows to millions.
- **Chroma** — Python-native, dead simple, but its persistence story (sqlite file or duckdb) duplicates what Postgres already gives us.
- **Weaviate** — overkill; great hybrid search but heavy.
- **Pinecone** — hosted-only is a non-starter for a self-hosted personal app. Also costs money for zero benefit at this scale.
- **LanceDB** — interesting, very fast on local files, but yet another data store.

## Recommendation

**pgvector. No contest at this scale.**

Implementation:
- Alembic migration: `CREATE EXTENSION IF NOT EXISTS vector;`
- Add `embedding vector(1024)` column to `news_articles` (or a sibling `news_embeddings` table if we want to support multiple embedding models in parallel).
- HNSW index: `CREATE INDEX ON news_articles USING hnsw (embedding vector_cosine_ops)`.
- Hybrid retrieval: `ORDER BY (0.5 * cosine_distance + 0.5 * (1 - bm25_score))` — one SQL query, no extra service.

Rationale:
- Zero new infrastructure. Postgres is already running and trusted.
- Joins between articles and embeddings happen in-DB — no app-level cross-store coordination.
- Migration to a dedicated vector DB later is a non-issue (just a different fetch path) if the corpus grows beyond Postgres's comfort zone (~10M vectors).

## Open questions

- Embedding dimension: 1024 (Voyage), 1536 (OpenAI), 3072 (OpenAI v3 large)? See [10](10-embedding-model.md). pgvector supports up to ~16k dims as of 0.7.
- HNSW vs IVFFlat? HNSW is better-recall-per-millisecond at our scale; IVFFlat is older and not worth choosing.
- Chunking strategy: per-article (one vector per article) vs paragraph-chunked? Probably paragraph for news, since users ask about specific quotes.
- Re-embed on model upgrade — keep an `embedding_model_version` column so we can migrate without dropping the table.
