# 05 — Memory Store

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | PostgreSQL only | Free (already running) |
| **Chosen** | **PostgreSQL only** — matches the recommendation and the plan. | ₹0 |

No deviation. Already aligned with the zero-paid-services constraint.

---

## Context

The plan ([1-concierge-plan.md](../1-concierge-plan.md)) already specifies PostgreSQL for `concierge_sessions` + `concierge_turns`. This doc validates that choice against the alternatives and surfaces the cases where a hybrid would matter.

## Options

| Store | Persistence | Latency for load_history | Ops cost | Already in stack? |
|---|---|---|---|---|
| **PostgreSQL** | Durable | ~5–15ms for 20 rows | Already running | Yes |
| **SQLite** | Durable (single file) | ~2–5ms | Zero | Yes (Wagner uses it) |
| **Redis** | In-memory + AOF | <1ms | New service | No |
| **PostgreSQL + Redis (hybrid)** | Durable + hot cache | <1ms when hot, ~10ms cold | New service | Partial |
| **In-process dict + WAL** | Crash-recoverable | <0.1ms | Zero | No |

## Tradeoffs

- **PostgreSQL** — boring, durable, transactional. The 5–15ms load is dwarfed by the 1–3s Claude inference call, so latency doesn't matter. Already running for portfolio data. Free.
- **SQLite** — would also work; Wagner uses it for IAM. Splitting concierge into a separate file (vs. living in the main Postgres) creates two transaction domains, which complicates anything that ever joins users + sessions. Don't fork.
- **Redis** — the only reason to add Redis is sub-millisecond load latency, which is invisible against Claude's response time. Adds an ops surface for zero perceptible win. Skip.
- **Hybrid Postgres + Redis** — useful if multi-user with many concurrent sessions where Postgres connection pool becomes a bottleneck. Anton is single-user. Not yet.
- **In-process dict + WAL** — what the *current* frontend implementation effectively is (the 6-turn React state). Loses on refresh, doesn't survive restarts. The whole point of this upgrade is to leave this behind.

## Recommendation

**PostgreSQL only, as already specified in the plan.**

Rationale:
- Single-user single-tenant: Redis adds zero value at this scale.
- All other Anton data lives in Postgres; keep the data model coherent.
- The plan's Alembic migration is already drafted ([c7a3e9f1d2b8_concierge_memory.py](../../backend/alembic/versions/c7a3e9f1d2b8_concierge_memory.py) referenced in README).
- Reconsider Redis only if (a) Anton grows to multi-user, AND (b) Postgres pool contention shows up in real profiling.

## Indexing notes

Worth specifying upfront so the migration includes them:

| Index | On | Purpose |
|---|---|---|
| Primary key | `concierge_sessions.id`, `concierge_turns.id` | Standard |
| `idx_turns_session_created` | `(session_id, created_at DESC)` | Backs `load_history` query |
| `idx_sessions_user_updated` | `(user_id, updated_at DESC)` | Future session list UI |

## Open questions

- Should the system prompt + cached context be versioned in a separate table so we can replay a session against a different prompt later? (Probably overkill for now.)
- Retention policy: keep all sessions forever, or auto-archive after N months? Single-user use means storage is trivial — keep forever.
- Do we need a `concierge_tool_calls` table to log tool-use invocations? Useful for debugging but adds schema surface. Defer until tool-use is actually built.
