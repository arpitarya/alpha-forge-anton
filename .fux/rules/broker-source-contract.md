---
id: broker-source-contract
domain: brokers
type: convention
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/base.py
  - backend/app/modules/brokers/registry.py
related: [broker-source-integration, dump-utils-single-source, holdings-sum-equals-total, files-max-100-lines]
keywords: [broker, source, adapter, fetch, sync, slug, registry, lifecycle]
---
**Convention:** Every holdings provider is a `BrokerSource` subclass
([base.py](../../backend/app/modules/brokers/base.py)) that sets the three class
attributes `slug`, `label`, `kind`, overrides `async def fetch() -> list[Holding]`,
and is registered exactly once in
[registry.py](../../backend/app/modules/brokers/registry.py)'s `_build_sources()`.
The source **never** manages its own status or cache — lifecycle (`SYNCING →
READY/ERROR`, `_cached`, `_last_synced_at`) is owned by `BrokerSource.sync()`.

**Why:** the aggregator and routes treat every source through this one interface,
so the roll-up ([[holdings-sum-equals-total]]), `/portfolio/*` endpoints, and the
UI's source list all work the moment a source is registered — no per-broker special
casing. A source that mutates `self._status` directly, caches holdings itself, or
skips `sync()` breaks the status state machine and the never-synced startup prime
([[project-broker-prime]]).

**How to apply:** subclass `BrokerSource`; put auth + raw fetch in
`{slug}_source_helper.py`, CSV caching in `{slug}_dump.py` (thin wrapper over
`dump_utils`, see [[dump-utils-single-source]]), and credential keys in
`REQUIRED_ENV` gated by `source_ready()` (see [[vault-only-credentials]]). Opt into
cash by setting `supports_cash = True` and overriding `fetch_cash()`. Set
`currency = "USD"` for non-INR brokers. Each file stays ≤100 lines
([[files-max-100-lines]]). Full walkthrough: [[broker-source-integration]].
