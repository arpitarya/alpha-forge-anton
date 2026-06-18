# Runtime money/PII critic (Orff live-write guard)

The `plan-store` constitutional rule blocks money documents and hard PII at the **commit**
boundary (`dante pii` + `just probe plan-safety` + the required `fux gate` CI check). But Orff
writes to the private **elgar** store **at runtime** — from free agent/user text — where no
pre-commit hook runs. A note carrying a PAN would be persisted with one git commit and become a
real, irreversible PII leak into the money store.

The **runtime critic** closes that hole on the single riskiest live path, mirroring fux's
deterministic/judgment split. It is the runtime twin of `plan-store`; the Fux principle is
[`runtime-note-pii`](../.fux/rules/runtime-note-pii.md) (`fux why runtime-note-pii`).

## Scope (deliberately narrow)

**One path: `append_memory`** — the `orff-context` memory note. `set_objective` and
`save_action_plan` are **not** guarded by this principle yet. Widening is a separate, reviewed
step — do not extend the guard to a new path until this one is proven in production.

## The two layers

| Layer | What | Blocks? | Cost |
| ----- | ---- | ------- | ---- |
| **Deterministic** | `critic_guard.review_note` — the same PAN / Aadhaar / account-number BLOCK patterns as `sentinel/pii_scanner` (`dante pii`) | **Always** — raises `ForbiddenRuntimeAction` → HTTP 422, the elgar save never runs | `$0`, in-process, no LLM |
| **Judgment** | `fux critic "<note>"` via `fux_bridge.critic_suggestions` — surfaces money/PII *judgment* principles for host-agent self-critique | **No** (advisory-first, fux ≥ 0.5.0) — logged, not blocked, until escalated via `critic_block_judgment` | tokens metered by **Cage** at the LLM gateway |

The deterministic classes are **not opinions** — they refuse, they do not advise. Advisory-first
on the judgment side is the trust lever: the critic earns its way to blocking before it interrupts.

## Code path

```
POST /api/v1/concierge/memory/append   (tool_routes.post_memory_append)
  └─ memory_service.append_memory(note)
       └─ critic_guard.guard_note(note)              # BEFORE any write
            ├─ _deterministic_block(note)            # PAN/Aadhaar/account → raise → 422
            └─ fux_bridge.critic_suggestions(note)   # advisory, best-effort, $0 unless LLM runs
       └─ elgar_bridge.save(...)                      # only reached if the guard cleared
```

- Guard: [backend/app/modules/concierge/critic_guard.py](../backend/app/modules/concierge/critic_guard.py)
- Bridge: [backend/app/modules/concierge/fux_bridge.py](../backend/app/modules/concierge/fux_bridge.py) (`critic_suggestions`)
- Call site: [backend/app/modules/concierge/memory_service.py](../backend/app/modules/concierge/memory_service.py) (`append_memory`)
- Route: [backend/app/modules/concierge/tool_routes.py](../backend/app/modules/concierge/tool_routes.py) (422 on refusal)

## Verification

```bash
just probe critic-runtime
```

Attempts the forbidden runtime action — appending notes with a PAN, an Aadhaar, and an account
number — and asserts each is refused **before** the elgar save (no write escapes), while clean
strategy/preference notes pass. Exit 0 on full pass. This is the runtime sibling of
`just probe plan-safety` (which guards the commit boundary).

## Why advisory-first, and why so narrow

A judgment critic that blocks on day one gets turned off; an over-broad guard that fires on every
mutation gets routed around. Start with **one** path where the deterministic block is unarguable
(hard identifiers in a persisted note), keep the judgment layer advisory, prove it, then widen.
The cost of narrowness now is the credibility to widen later.
