---
id: elgar-mandate
domain: security
type: convention
status: active
tier: constitutional
created: 2026-06-28
updated: 2026-06-29
keywords:
  - elgar
  - money-store
  - plans
  - pii
  - two-place-rule
  - private
  - delegation
code_refs:
  - backend/app/core/paths.py
  - backend/app/modules/plans/elgar_bridge.py
  - backend/app/modules/plans/elgar_store.py
  - backend/app/modules/plans/plan_loader.py
  - backend/app/modules/signals/objective_loader.py
  - backend/app/modules/signals/config_loader.py
  - backend/app/modules/signals/objective_tuning.py
  - backend/app/modules/signals/strategy_tuning.py
  - backend/app/modules/goals/mandate_loader.py
  - backend/app/modules/edges/edge_journal.py
  - probes/elgar_store_guard_probe.py
related:
  - plan-store
  - knowledge-location
  - configurable-paths
seal: 5044e48b80a12141
ratification:
  by: Arpit
  date: 2026-06-29
  content_seal: 77f0fc840af4f0ed
---
# Elgar mandate — the suite's private money store

**Constitutional:** **Elgar is the canonical home for money knowledge.** Every
money document — personal financial plans, portfolio **strategy** plans
(targets/bands/rules), projections, and saved Orff plan conversations — together
with all **hard PII** lives in the **elgar** store, never inlined into a public
repo. Public repos (Anton, the `.fux/` substrate) hold only `elgar://plan/<id>`
**links**, never content.

Which home a document belongs to is decided by **one test** ([[knowledge-location]]):
*does it change with my money → elgar; with the world or the code → `.fux`.*

**Delegation — Anton owns no elgar path (merged from `anton-delegates-elgar-store`):**
Anton holds **no** elgar filesystem path. The elgar sibling tool owns the store
**and** its path; Anton reaches the store only through the elgar CLI API
(`app.modules.plans.elgar_bridge` — `save` / `get` / `get_sync` / `list_docs`;
plus `elgar_store.store_root`, obtained from `elgar path`, for the few raw
`json` / `jsonl` files the doc API doesn't serve). Every write is **fail-loud**: a
bad or unreachable store raises `ElgarStoreError`, never a silent fallback to a
local directory. `ELGAR_DIR` is therefore configured on the **elgar** side, not
Anton (Anton's only elgar env var is `ELGAR_BIN`, which locates the executable).
This is a deliberate, documented **exception to [[configurable-paths]]'**
derive-from-`ANTON_DATA_DIR` obligation: the store is externally owned, so a path
Anton computes for it is the bug — a stale `ELGAR_DIR` once let direct-file
writers (objective / strategy config, the edge journal `jsonl`) write to a
non-store directory while elgar's own self-validating writes failed loud, orphaning
money/strategy docs outside the real store. Guard: `just probe elgar-store-guard`.

**Storage facts (as shipped, `elgar/src/elgar/store.py`):** the store is
git-versioned — **one git commit per save**, so history / diff / rollback come
from git (`elgar history <id>`) — created at mode **0700**, with its root
configured on the elgar side via **`ELGAR_DIR`**. By **default** the store is a
`store/` collection **inside the elgar source repo**, sharing that repo's git
history (`_REPO_ROOT`); pointing `ELGAR_DIR` at a standalone private repo is what
makes it physically separate. *(The store is therefore only as private as the repo
that holds it — keep the elgar source repo private, or relocate the store via
`ELGAR_DIR`. Do not describe it as "outside any public tree" by default — the code
does not provide that.)*

**Why:** A leaked plan or identifier exposes a real person's net worth and
allocations — an irreversible leak, not a fixable bug. Naming elgar the single
home, the two-place test the placement law, and the elgar CLI the single
audited door keeps money knowledge from scattering into home-dir packs, loose
files, or an Anton-computed shadow path. The invariant never legitimately changes;
only the storage mechanism may evolve, which is why the mechanism is described as
fact, not sealed as the invariant.

**Enforcement:** the *public-repo boundary* — the part whose violation costs PII —
is the always-blocking, deterministically-gated invariant, enforced by
[[plan-store]] (`dante pii` CRITICAL/HIGH → BLOCK + `just probe plan-safety`,
wired into pre-commit **and** the required `just constitution` / `fux gate` CI
check). The *delegation* invariant is guarded by `just probe elgar-store-guard`.
This mandate is the affirmative charter; `plan-store` is its wall.

**How to apply:**
- Save/edit a plan → `elgar save <id> -f <file>` (or stdin); never write a
  `*.plan.md` / `*.drift.md` inside a public repo.
- Read a plan in code → `app.modules.plans.elgar_bridge` (`get_sync`) /
  `plan_loader`; never compute an elgar path inside Anton.
- Reference a plan in a Fux entry → a stub whose body is the `elgar://plan/<id>` URI.

**Debate & amendment:** ratified over a recorded two-agent dissent (both voices
recommended *not* creating a separate constitutional rule — it overlaps
[[plan-store]] and [[knowledge-location]], and the original wording's "private repo
outside any public tree" is contradicted by `store.py` — see
`.fux/debates/elgar-mandate.md`). The human ratifier overruled on tier; the false
claim was corrected rather than sealed. **2026-06-28:** the standard ADR
`anton-delegates-elgar-store` was merged into this constitutional rule (its
decision, consequences, and `code_refs`) and removed; this rule was re-ratified to
re-stamp the seal.

## Related

[[plan-store]] · [[knowledge-location]] · [[configurable-paths]] · [[context-docs-figure-free]] · [[secure-holdings-plan]]
