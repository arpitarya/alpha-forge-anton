---
id: project-broker-prime
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-05-25
updated: 2026-06-03
---
`backend/app/modules/brokers/refetch.py` runs a one-shot `_prime_unsynced` task at FastAPI startup that calls `sync()` on every `SourceStatus.READY` broker source whose `_last_synced_at` is None. Fire-and-forget (asyncio.create_task without await) so slow CDP-based sources don't block app startup.

**Why:** the refetch loop's `_is_due` deliberately skips never-synced sources to avoid hammering a broken source every 60s. Before the prime task, every fresh DB / new broker showed zero holdings in the UI until the user manually clicked Sync — silent failure, no error anywhere. This pattern bit Zerodha (2026-05-25) and is likely to bite any new broker the same way.

**How to apply:** if a broker shows zero holdings and `last_synced_at: null`, *don't* assume the source is broken — first check the backend log around lifespan startup for `Prime: <slug> failed —` warnings. The failure detail is the real bug. If priming succeeds, the recurring refetch loop takes over normally.

Related: [[project-wagner-dante]].
