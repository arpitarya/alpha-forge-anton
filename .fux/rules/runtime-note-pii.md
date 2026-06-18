---
id: runtime-note-pii
domain: security
type: invariant
status: active
principle: money/PII
enforcement: deterministic
created: 2026-06-18
updated: 2026-06-19
aliases:
  - runtime-pii-guard
  - orff-note-guard
  - critic-runtime-block
keywords:
  - pii
  - runtime
  - critic
  - orff
  - memory
  - note
  - pan
  - aadhaar
  - account
  - block
  - advisory
code_refs:
  - backend/app/modules/concierge/critic_guard.py
  - backend/app/modules/concierge/memory_service.py
related:
  - plan-store
  - mutation-confirm-rmw
  - context-docs-figure-free
  - secure-holdings-plan
seal: a2ab8247054bca0e
---
**Principle (deterministic — runtime money/PII guard):** Any text the Orff agent writes
into a **persisted money-adjacent document at runtime** — starting with the `orff-context`
memory note (`append_memory`) — is critiqued **before** it is saved. Hard identifiers
(**PAN**, **Aadhaar**, **broker account / client / folio numbers**) are an **always-blocking**
deterministic refusal: the write never reaches the elgar store. This is the runtime twin of
[[plan-store]], which blocks the same classes at **commit** time.

**Why:** `plan-store` makes a leak impossible *into the public repo*. But Orff writes to the
elgar store **at runtime**, from free agent/user text, where no pre-commit hook runs — a note
carrying a PAN is persisted with one git commit and is then a real, irreversible PII leak into
the money store. The same BLOCK classes the audit enforces at the commit wall must also hold at
the runtime write boundary, or the constitutional guarantee has a live hole the size of the chat
box. The deterministic classes are not opinions; they refuse, they do not advise.

**How it's enforced:**
- **Deterministic (block):** `critic_guard.review_note(note)` runs the same hard-identifier
  patterns as `sentinel/pii_scanner` (PAN `[A-Z]{5}[0-9]{4}[A-Z]`, Aadhaar `\d{4}\s\d{4}\s\d{4}`,
  `account|a/c|client_id|folio` + ≥6 digits). A match raises `ForbiddenRuntimeActionError`; the elgar
  save is never called. `$0`, in-process, no LLM.
- **Judgment (advisory, at first):** after the deterministic pass clears, the guard calls
  `fux critic "<note>"` (via `fux_bridge`) to surface money/PII *judgment* principles for
  host-agent self-critique. Advisory-first (fux ≥ 0.5.0): a judgment concern is logged, not
  blocked, until a principle is escalated via `critic_block_judgment`. Any tokens this spends are
  metered by **Cage** at the LLM gateway.

**Scope (do not widen until proven):** `append_memory` only. `set_objective` /
`save_action_plan` stay un-guarded by this principle until the one path is proven in production.
Widening is a deliberate, separately-reviewed step — see [[mutation-confirm-rmw]].

## Related

[[plan-store]] · [[mutation-confirm-rmw]] · [[context-docs-figure-free]] · [[secure-holdings-plan]]
