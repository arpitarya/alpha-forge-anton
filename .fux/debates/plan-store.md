# Debate — `plan-store` → constitutional

**Proposed rule:** "never commit money docs or PII; plans live in elgar"
**Tier sought:** constitutional (apex — always-blocking, sealed)
**Date:** 2026-06-17
**Format:** two-agent free debate (anti-sycophancy). Both agents briefed identically,
side-free, blind to each other's first pass. Human is tie-breaker + ratifier.

---

## Blind first pass — Agent A

**Position: ADOPT-AMENDED.**

The *intent* of `plan-store` belongs at the apex — a public MIT repo where a leaked plan
exposes a real person's net worth and allocations is a "wrong by construction" risk, exactly
what a sealed, always-blocking rule is for. But the proposed wording — "never commit money
docs or PII" — is broader than what the codebase actually enforces, and that gap turns a
constitutional rule into a liar.

**Objection (concrete failure mode):** Making "never commit … PII" *always-blocking*
contradicts the shipped enforcement. Dante's pii scanner classifies `inr-amount` as
MEDIUM / WARN, with an explicit carve-out: grouped ₹ amounts are WARN-only because docs
legitimately carry worked examples. A constitutional always-block rule would either (a) demand
the scanner be flipped to BLOCK on `inr-amount`, which immediately breaks commits touching
`docs/WHY.md` (`₹15-20 lakh/year` — a Bloomberg *pricing* illustration), `.fux/rules/day-pnl.md`,
`concierge/llm/eval/questions.yaml`, and the orff-tool-calling handoff — none of which are
personal data; or (b) leave the scanner as WARN, in which case the apex rule is unenforced
theater. Both are worse than today.

**Amended wording proposed by A:**
> Personal financial documents and hard personal identifiers must never enter this public repo
> (including `.fux/`). Always-blocking: (1) `*.plan.md` / `*.drift.md` plan documents — plans live
> in elgar (`elgar://plan/<id>` links only); (2) PAN, Aadhaar, and broker account/client/folio
> numbers; (3) real holdings figures (share counts, position ₹ values, live P&L). Illustrative
> example ₹ amounts in docs and eval fixtures are permitted and remain WARN-only; mark intentional
> lines `pii:allow`.

## Blind first pass — Agent B

**Not completed.** The host operator interrupted Agent B's run before it returned. Per the
fux-debate anti-sycophancy procedure, the host session served as the adversarial second voice
(the skill's stated model: "the intelligence is this host session's tokens"). A's objection was
independently **verified against source** before being relied on — `dante/README.md:70-72`:
`*.plan.md`/`*.drift.md` → CRITICAL block; PAN/Aadhaar/account-ids → HIGH block; grouped ₹
amounts → MEDIUM warn (`pii:allow` whitelists a worked example). Severity→verdict mapping:
CRITICAL/HIGH → BLOCK, MEDIUM/LOW → WARN. A's claim holds.

---

## Adversarial round

**Host → A's clause (3):** Clause (3) — "real holdings figures (share counts, position ₹ values,
live P&L)" as *always-blocking* — reintroduces the exact contradiction A just diagnosed. The pii
scanner cannot deterministically distinguish a *real* ₹ holding from an *example* ₹ figure; that
indistinguishability is precisely why grouped amounts are MEDIUM/WARN, not BLOCK. So an
"always-blocking" clause (3) is unenforceable by the tooling that backs the constitution — the
same theater A objected to, one clause down.

**Resolution (converged):** The constitutional, always-blocking core must bind only to what the
pii audit deterministically BLOCKs:
1. **Money documents** — `*.plan.md` / `*.drift.md` and any saved plan/projection content
   (CRITICAL block). These live only in elgar; the repo holds `elgar://plan/<id>` links.
2. **Hard identifiers** — PAN, Aadhaar, broker account / client / folio numbers (HIGH block).

Real position figures stay *out* by construction: the document that would carry them is a plan
(class 1, blocked), and figures in standing-context/memory docs are already governed by
[[context-docs-figure-free]]. So "no real holdings figures" is preserved as a linked consequence,
**not** as a fourth always-blocking ₹-pattern the scanner can't honour. Illustrative example ₹
amounts in docs / knowledge rules / eval fixtures remain MEDIUM/WARN, whitelisted per line with
`pii:allow`.

Both voices tried to break the rule (A broke the original wording; host broke A's amendment).
Convergence reached only after the second falsification. Constitutional-tier extra adversarial
round satisfied.

---

## Agreed final wording (to seal)

> **Constitutional:** Personal financial **documents** and **hard personal identifiers** must
> never enter this public repo (including the `.fux/` substrate). Two always-blocking classes,
> matched to the `dante pii` BLOCK tier:
> 1. **Money documents** — `*.plan.md` / `*.drift.md` and any saved personal plan, strategy plan
>    (targets/bands/rules), projection, or saved Orff plan conversation. These live only in the
>    **elgar** store (`ELGAR_DIR`, default `~/.alphaforge-anton/elgar`); this repo holds
>    `elgar://plan/<id>` links, never content. (CRITICAL → BLOCK.)
> 2. **Hard identifiers** — PAN, Aadhaar, and broker account / client / folio numbers.
>    (HIGH → BLOCK.)
>
> Illustrative / worked-example ₹ amounts in docs, knowledge rules, and eval fixtures are
> permitted (MEDIUM → WARN); whitelist an intentional line with `pii:allow`. Real position
> figures (share counts, holding ₹ values, live P&L) belong in elgar / live disclosure and are
> kept out by class 1 above + [[context-docs-figure-free]] — they are never committed.
>
> **Enforcement (required CI gate, not just local):** `dante pii` (CRITICAL/HIGH → BLOCK) +
> `just probe plan-safety`, wired into pre-commit **and** the required `just constitution`
> (`fux gate`) CI check. Local pre-commit is bypassable with `--no-verify`; CI is the wall.

## Residual risks

- **Coarse ₹ detection.** A determined leak of a *real* figure phrased as prose ("about fifteen
  lakh") evades the regex. The constitution blocks the document class and hard identifiers
  deterministically; semantic leakage of a stray number remains a review concern, not a
  gate guarantee. Accepted — sealing the document/identifier classes is the irreversible-leak
  surface; stray-number prose is lower-blast-radius and review-caught.
- **`pii:allow` abuse.** The whitelist could be used to wave a real figure past the gate.
  Mitigated by: it only downgrades MEDIUM ₹ warns (never the CRITICAL/HIGH blocking classes),
  and each use is a visible diff line.
