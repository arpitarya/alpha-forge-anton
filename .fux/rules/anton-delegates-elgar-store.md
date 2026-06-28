---
id: anton-delegates-elgar-store
domain: security
type: adr
status: deprecated
created: 2026-06-28
updated: 2026-06-28
related:
  - elgar-mandate
  - configurable-paths
  - plan-store
---
**Merged into [[elgar-mandate]] (constitutional) on 2026-06-28.**

This ADR's decision — Anton holds **no** elgar filesystem path; all elgar I/O goes
through the elgar CLI API (`elgar_bridge` / `elgar_store.store_root`); every write
is fail-loud (`ElgarStoreError`, never a silent local fallback); `ELGAR_DIR` is
configured on the **elgar** side (Anton keeps only `ELGAR_BIN`); a deliberate
exception to [[configurable-paths]] because the store is externally owned — now
lives in the constitutional rule [[elgar-mandate]], along with its `code_refs` and
the `just probe elgar-store-guard` guard.

Retained as a tombstone so the original decision id resolves; see [[elgar-mandate]]
for the active, sealed statement.
