---
id: dump-utils-single-source
domain: brokers
type: convention
status: active
created: 2026-06-09
updated: 2026-06-27
keywords:
  - csv
  - dump
  - cache
  - dump_utils
  - ttl
  - path
  - headers
  - single-source
code_refs:
  - backend/app/modules/brokers/dump_utils.py
related:
  - broker-source-contract
  - broker-csv-dumps
  - inr-normalization
---
**Convention:** All broker CSV I/O goes through
[dump_utils.py](../../backend/app/modules/brokers/dump_utils.py) — path resolution
(`live_csv_path`, `dated_csv_path`), freshness (`is_csv_fresh`), reads (`read_csv`),
writes (`write_csv`), file permissions, the canonical header set, and P&L
computation. A `{slug}_dump.py` is only a thin TTL-aware wrapper that forwards to
these functions; it never opens, formats, or `chmod`s a CSV itself.

**Why:** the dump directory (`$PORTFOLIO_DUMP_DIR` or
`~/.alphaforge-anton/portfolio-dumps/`), the `0600` permissions on files that hold
financial positions, the exact column order the readers expect, and the
`qty×avg / qty×ltp / pnl` math must be identical across every broker. One source
hand-rolling its own CSV is how columns drift, a cache silently goes stale, or a
dump lands world-readable. Centralising it makes the contract a single auditable
file ([[broker-csv-dumps]]).

**How to apply:** import the five helpers from `dump_utils` (see the template in
[[broker-source-integration]]) and pass `source={slug}` to `write_csv`. Need a new
column or a different freshness rule? Change `dump_utils.py` once, not per broker.
Monetary values are INR-normalised downstream by the aggregator
([[inr-normalization]]), so the CSV stores each holding in its source currency.
