---
id: fux-mandate
domain: governance
type: convention
status: active
tier: constitutional
created: 2026-06-28
updated: 2026-06-28
keywords:
  - fux
  - knowledge-engine
  - deterministic
  - no-llm
  - version-pin
code_refs:
  - pyproject.toml
seal: b3f0ea94f987ffd7
ratification:
  by: arpit arya
  date: 2026-06-27
  content_seal: 041a6d2556369671
  debate_hash: 669c99c46fbc70cc
---
# Fux mandate — the suite's knowledge engine, bound to a $0 / deterministic / no-LLM version

**Constitutional:** Anton's knowledge layer is **Fux** — version-controlled,
code-bound rules that record *why* the code is the way it is (invariants,
formulas, decisions), read before any edit and warned when the code drifts from
the rule. Anton MUST remain pinned to a Fux version whose maintenance / derive /
check path is **`$0`, deterministic, stdlib-only, with no mandatory LLM call**.
Intelligence (debate, critic judgement) spends the *host session's* tokens; Fux's
own code never calls a model.

The guarantee is **owned and enforced upstream** by the fux repo's own no-LLM
guard test — anton cannot seal code it does not contain. Anton holds the
guarantee through its **one real lever: the exact version pin**
([[fux-engine-exact-pin]]). Every fux bump is reviewed against this invariant; an
upgrade that introduces a mandatory model call on the maintenance/derive/check
path **must be rejected at bump review.** That review gate — not a seal over a
foreign repo's behaviour — is what this rule binds.

**Why:** A knowledge layer is only trustworthy because it is deterministic — it
never hallucinates because it never guesses, so an agent can act on it and an
auditor can stand behind it. A Fux that phoned a model on `fux check` would make
the apex itself non-reproducible and the whole governance story circular. The
invariant never legitimately changes: the day it does, "verifiable, governed
code-context" stops being true of this suite. Sealing it at the version-pin lever
keeps the rule enforceable rather than theatrical.

**How to apply:**
- Depend on Fux only via the exact pin in `pyproject.toml` ([[fux-engine-exact-pin]]).
- On any fux upgrade, confirm upstream's `$0`/no-LLM guard test still passes for
  the new version before bumping; reject the bump otherwise.
- Use `fux why` / `fux refs` / `fux check` as the read+drift surface; never route
  a maintenance command through a model.

**Debate:** ratified over a recorded two-agent dissent (both voices recommended
`standard`, not constitutional — see `.fux/debates/fux-mandate.md`). The human
ratifier overruled: the invariant is constitutional in kind, and binding it to
the version-pin lever answers the "unenforceable from anton" objection.

## Related

[[fux-engine-exact-pin]] · [[knowledge-location]] · [[plan-store]]
