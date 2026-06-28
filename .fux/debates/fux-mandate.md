# Debate — `fux-mandate` → constitutional (proposed)

**Proposed rule:** "Fux is the suite's knowledge engine: it records WHY code is the
way it is, and its maintenance/derive path is constitutionally bound to remain $0,
deterministic, stdlib-only, with no mandatory LLM call. Adopting Fux changes nothing
until a rule is ratified."
**Tier sought:** constitutional (apex — always-blocking, sealed)
**Date:** 2026-06-28
**Format:** two-agent free debate (anti-sycophancy). Both agents briefed identically,
side-free, blind to each other's first pass. Human is tie-breaker + ratifier.

---

## Blind first pass — Agent A

**Position: REJECT as constitutional** (adopt-amended only if reframed to `standard`).

Both prongs of the constitutional test fail. The existing sealed rules (`plan-store`,
`configurable-paths`) are constitutional because a *deterministic gate inside anton's CI*
(`dante pii`, `just constitution`, `fux gate`) refuses to merge a violation. `fux-mandate`'s
core claim — "$0/stdlib/no mandatory LLM" — is a property of the **fux source repo**, governed
there by its own guard test (fux README: "a guard test proves it"). Anton's `.fux/` substrate
cannot seal or check a guarantee about code it does not contain. `fux-engine-exact-pin` only
pins a *version string* in `pyproject.toml`; it cannot assert anything about that version's
internal model-call behaviour.

**Objection (concrete):** anton's substrate cannot verify the rule's central claim — there is
no `check:`/seal anton can run to prove fux's derive path made no LLM call. Ratifying would
stamp a `content_seal` on a sentence anton has no deterministic way to falsify — *"a
constitutional rule whose tooling refuses to block half of it would be theater"* (plan-store
rationale, the project's own bar). Secondary cost: overlaps `fux-engine-exact-pin` without
superseding it. The trailing sentence ("adopting Fux changes nothing until ratified") is a
*description of fux's default*, not an anton invariant — it changes if fux changes its default,
failing prong two.

**Amended wording (as `standard`):** keep the charter, but move the enforcement claim to where
it is true (the fux repo's guard test) and bind anton's one real lever — the exact version pin
([[fux-engine-exact-pin]]); reject upgrades that weaken the no-LLM guarantee at bump review.

## Blind first pass — Agent B

**Position: REJECT as constitutional** (adopt as `standard` + `narrative`).

*Cost-of-wrong-answer:* `plan-store`/`configurable-paths` describe per-commit actions where a
wrong answer directly leaks PAN/Aadhaar or hard-codes a money path. `fux-mandate` describes a
property of a *different repo's* source; a "wrong answer" (fux adds an LLM call upstream) moves
no money, leaks no PII, falsifies no audit record *in anton*. Blast radius is an upstream
build-cost regression — which `fux-engine-exact-pin` already contains.

*Never-legitimately-changes:* the $0/stdlib guarantee is fux's product positioning, owned by
fux's README and its guard test; fux even reserves a `[critic]` extra, explicitly contemplating
evolving its model-touching surface. A charter the governed party can legitimately revise is, by
definition, a `standard` rule.

**Objection (load-bearing):** unenforceable theater at the apex. `fux gate`/`fux check` seal an
AST fingerprint of code *in this repo*; the no-LLM property lives entirely in the fux repo. So
`constitution.lock` would stamp a seal over prose nobody local can check — anton would detect
tampering of the *sentence* while structurally blind to the *fact*. It would be the first
constitutional rule here binding to nothing local — a precedent that hollows out "constitutional."

**Amended wording (as `standard`, `type: principle`, + narrative companion):** Anton's knowledge
layer is Fux; we adopt it on the upstream-verified understanding that its maintenance path is
$0/deterministic/stdlib/no-mandatory-LLM, enforced by the fux repo's guard test, trusted via the
exact version pin. Promote to constitutional only if a wrong answer here ever costs anton money,
PII, or audit.

---

## Adversarial round (host)

Both agents converged *independently* and *blind* on the same verdict: the boundary the proposed
rule asserts is real, but it is not anton's to seal, because anton's deterministic tooling cannot
falsify it. I tried to break the convergence: could anton add a `check:` that imports fux and
asserts no network/model symbol on the derive path? No — that tests the *installed* version's
surface, not a guarantee, and would be a fragile import-time heuristic, not a seal of fux's
source. The objection holds. Convergence reached only after attempting falsification.

## Converged outcome

**Do not ratify `fux-mandate` as constitutional.** The honest forms are:
1. A `standard` charter rule recording what Fux is + the upstream guarantee, binding anton's one
   real lever ([[fux-engine-exact-pin]]); promote only if a wrong answer ever costs anton
   money/PII/audit. **(verifiable, honest)**
2. The $0/no-LLM *invariant itself* is constitutional — **in the fux repo's own `.fux/`**, where
   its guard test is the deterministic check that backs the seal.

## Residual risk

- A `standard` charter in anton is not gate-enforced; it is documentation + the pin lever. That is
  the correct enforcement surface for a cross-repo dependency — overclaiming at the apex was the
  failure mode this debate removed.
