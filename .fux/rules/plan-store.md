---
id: plan-store
domain: security
type: convention
status: active
tier: constitutional
created: 2026-06-12
updated: 2026-06-17
ratification:
  by: arpit arya
  date: 2026-06-17
  content_seal: e43f9a09d216f31e
  debate_hash: 88ffc9f6a3abc119
---
# Plan store (elgar) — money documents & hard PII never enter the public repo

**Constitutional:** Personal financial **documents** and **hard personal
identifiers** must never enter this public repo — including the `.fux/`
substrate. Two always-blocking classes, matched to the `dante pii` BLOCK tier so
the rule enforces exactly what it claims:

1. **Money documents** — `*.plan.md` / `*.drift.md` and any saved personal plan,
   portfolio **strategy** plan (targets/bands/rules), projection, or saved Orff
   plan conversation. These live only in the **elgar** store (`ELGAR_DIR`,
   default `~/.alphaforge-anton/elgar`, sibling tool `~/my_programs/elgar`); this
   repo holds `elgar://plan/<id>` **links**, never content. (CRITICAL → BLOCK.)
2. **Hard identifiers** — PAN, Aadhaar, and broker account / client / folio
   numbers. (HIGH → BLOCK.)

Illustrative / worked-example ₹ amounts in docs, knowledge rules, and eval
fixtures are permitted (MEDIUM → WARN); whitelist an intentional line with
`pii:allow`. Real position figures (share counts, holding ₹ values, live P&L)
belong in elgar / live disclosure and are kept out by class 1 above plus
[[context-docs-figure-free]] — they are never committed.

**Why:** Anton is a public repo; a leaked plan or identifier exposes a real
person's net worth and allocations — an irreversible leak, not a fixable bug.
Even "strategy-only" plan docs drift toward personal data over time (example
targets mirror real allocations; goals acquire ₹ figures). Sealing the document
and identifier classes makes the leak impossible by construction instead of
policed by review. Fux keeps repo/engineering knowledge; elgar keeps money
knowledge. The rule binds only to what the audit deterministically blocks — a
constitutional rule whose tooling refuses to block half of it would be theater.

**How to apply:**
- Reading a plan in code → `app.modules.plans.plan_loader` (reads `<store>/plans/`).
- Saving/editing a plan → `elgar save <id> -f <file>` (or stdin); never write a
  `*.plan.md` / `*.drift.md` inside this repo.
- Referencing a plan in a Fux entry → a stub entry whose body is the
  `elgar://plan/<id>` URI (see [[core-allocation]], [[portfolio-plan-template]]).
- Enforcement (required CI gate, not just local): `dante pii`
  (CRITICAL/HIGH → BLOCK) + `just probe plan-safety`, wired into the pre-commit
  hook **and** the required `just constitution` (`fux gate`) CI check — local
  pre-commit is bypassable with `--no-verify`; CI is the wall.

## Related

[[context-docs-figure-free]] · [[secure-holdings-plan]] · [[no-secrets-in-vcs]] ·
[[vault-only-credentials]] · [[afbach-vault]]
