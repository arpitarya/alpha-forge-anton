---
id: mutation-confirm-rmw
domain: architecture
type: rule
status: active
created: 2026-06-16
updated: 2026-06-16
code_refs:
  - backend/app/modules/concierge/tool_executor.py
  - backend/app/modules/concierge/action_service.py
  - backend/app/modules/concierge/memory_service.py
  - backend/app/modules/concierge/exclusion_service.py
related: [strategy-knob-tradeoffs, secure-holdings-plan, plan-store, ui-component-contract]
aliases: [confirm-card-mutations, approval-card-writes, no-silent-mutation]
keywords: [mutation, confirm, approval, rmw, append, intent, sync, build_confirm]
---
**Rule:** every Orff-initiated mutation (memory note, exclusion-list edit, strategy/objective
change, plan save) is **confirm-gated** and follows one shape:

1. **`build_confirm` stays sync and pure** — it emits a **minimal intent payload**
   (`{append: note}`, `{add: X}`, `{remove: X}`, `{set: …}`), never the merged document, and
   does **no I/O**.
2. **The executor owns the merge** — the apply handler does the **read-modify-write
   server-side**, atomically, one elgar git commit. The frontend never merges or writes back
   authoritative content.
3. **Confirm card represents the operation**, not a full-doc diff ("Append to your context:
   '…'"). A full-doc preview is only for true replacements (set-to-this).
4. **Verb honesty** — a non-idempotent append/add is `POST` (e.g. `POST /concierge/memory/append`),
   never a `PUT` that replaces. Never a `GET` with a body.

**Why:** keeps confirm cards synchronous and race-free, keeps the store the single source of
truth, and makes every change an auditable one-line commit — a rejected card writes nothing.

**How it's enforced:** the `action_service` confirm flow (`{confirm:{id,action,summary,steps}}`
→ user confirm → dispatch). Probes assert "add X" / "set target" write **only** after confirm
and a rejected card writes nothing. Mutating tools are trusted-lane only — see [[trusted-lane-tools]].
Money docs commit to the elgar store, never this repo — see [[plan-store]].
