---
id: plan-store
domain: security
type: convention
status: active
created: 2026-06-12
updated: 2026-06-12
---
# Plan store (elgar) — money documents are linked, never stored

**Convention:** Every money document — personal financial plans, portfolio
**strategy** plans (targets/bands/rules), projections, saved Orff plan
conversations — lives in the **elgar store**: a private git repo at `ELGAR_DIR`
(default `~/.alphaforge-anton/elgar`), managed by the sibling tool
`~/my_programs/elgar`. This public repo — including this `.fux/` substrate — may
hold only **links** of the form `elgar://plan/<id>`, never the content. Fux keeps
repo/engineering knowledge; elgar keeps money knowledge.

**Why:** Anton is a public repo. Even "strategy-only" plan docs drift toward
personal data over time (example targets mirror real allocations; goals acquire ₹
figures). Moving the whole class of documents out of the work tree makes the leak
impossible by construction instead of policed by review. Versioning still comes
from git — the store is its own repo, one commit per `elgar save`.

**How to apply:**
- Reading a plan in code → `app.modules.plans.plan_loader` (reads `<store>/plans/`).
- Saving/editing a plan → `elgar save <id> -f <file>` (or stdin); never write a
  `*.plan.md` / `*.drift.md` inside this repo.
- Referencing a plan in a Fux entry → a stub entry whose body is the
  `elgar://plan/<id>` URI (see [[core-allocation]], [[portfolio-plan-template]]).
- Enforcement: `just probe plan-safety` (no tracked plan docs, committed docs
  strategy-only) and Dante's `pii` audit (repo-wide personal-info scan, wired into
  the pre-commit hook).

## Related

[[secure-holdings-plan]] · [[no-secrets-in-vcs]] · [[vault-only-credentials]] ·
[[afbach-vault]]
