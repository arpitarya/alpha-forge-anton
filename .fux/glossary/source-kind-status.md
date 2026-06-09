---
id: source-kind-status
domain: brokers
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/broker_schemas.py
related: [broker-source, broker-source-contract, project-broker-prime, holding]
aliases: [SourceKind, SourceStatus, ready, unconfigured]
keywords: [kind, status, api, csv, ready, syncing, error, unconfigured]
---
**Term:** SourceKind / SourceStatus

**Definition:** Two enums on a [[broker-source]]. **SourceKind** is how data
arrives: `API` (the source has `fetch()` over CDP/HTTP) or `CSV` (upload-only, uses
`parse()`). **SourceStatus** is the lifecycle state surfaced to the UI:
`UNCONFIGURED` (missing credentials — see [[vault-only-credentials]]), `READY`
(credentials present, idle), `SYNCING` (a fetch is in flight), `ERROR` (last sync
threw). Transitions are driven by `BrokerSource.sync()`; never set by source code
directly. The startup prime ([[project-broker-prime]]) auto-syncs never-synced
`READY` sources.
