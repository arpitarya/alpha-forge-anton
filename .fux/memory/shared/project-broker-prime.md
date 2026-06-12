---
id: project-broker-prime
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-05-25
updated: 2026-06-12
---
`backend/app/modules/brokers/refetch.py` exposes `prime_in_background`, which fires a `_prime_unsynced` task that calls `sync()` on every `SourceStatus.READY` broker source whose `_last_synced_at` is None. Fire-and-forget (strong-ref'd in `_bg_tasks`) so slow CDP-based sources don't block the caller. It runs twice: at FastAPI startup, and from `boot_probes.probe_vault` whenever a mid-life `afbach unlock` promotes UNCONFIGURED sources to READY (added 2026-06-12 — promoted sources used to miss the startup run and sit 'linked · not synced' with zero holdings until a manual sync).

**Why:** the refetch loop's `_is_due` deliberately skips never-synced sources to avoid hammering a broken source every 60s. Before the prime task, every fresh DB / new broker showed zero holdings in the UI until the user manually clicked Sync — silent failure, no error anywhere. This pattern bit Zerodha (2026-05-25) and is likely to bite any new broker the same way.

**How to apply:** if a broker shows zero holdings and `last_synced_at: null`, *don't* assume the source is broken — first check the backend log around lifespan startup for `Prime: <slug> failed —` warnings. The failure detail is the real bug. If priming succeeds, the recurring refetch loop takes over normally.

Related: [[project-wagner-dante]].
