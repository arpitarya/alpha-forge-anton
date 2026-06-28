# The Alpha Forge Constitution

*The apex rules of the Anton suite — what each sibling tool must do, what is sealed, and what deliberately is not.*

This is a human-readable index of the constitutional tier. It is **not** the source of truth: the law lives in `.fux/rules/<id>.md`, sealed in `.fux/constitution.lock`, each ratified over a recorded debate in `.fux/debates/<id>.md`. If this document and a sealed rule ever disagree, the sealed rule wins. Run `fux why <id>` for the authoritative text, or `fux constitution` for live status.

As of 2026-06-28 the apex holds **six** ratified rules, lock present, in sync.

---

## How a rule becomes constitutional

A rule is constitutional **only if** a wrong answer costs **money, PII, audit, or trust** **and** the rule **never legitimately changes**. If either half fails, it is a `standard` rule, not apex.

Law is made by **debate → ratify → lock**, never by fiat:

1. **`/fux debate`** spawns two side-free, blind sub-agents who must each raise a concrete objection; an adversarial round follows; the human is tie-breaker and ratifier.
2. **`fux ratify`** stamps a `content_seal` + the transcript's `debate_hash`, freezes a code `seal`, and records the rule in `.fux/constitution.lock`. After that, any in-place edit is an always-blocking `tampered` finding.
3. To change a constitutional rule you **supersede + re-ratify** — never edit in place.

Two honesty rules these debates enforced, visible throughout the apex below:

- **Seal only what Anton can enforce.** A guarantee that lives in a sibling repo (elgar's storage, fux's no-LLM guard, bach's KDF, wagner's token rotation) is cited as *fact*, never sealed at Anton's apex — sealing it would be theater.
- **Never seal a falsehood.** Where proposed wording contradicted the shipped code, the wording was corrected before sealing, not the other way around.

---

## The placement law — the two-place rule

Every durable fact has exactly one home, decided by one test (`knowledge-location`):

> **Does this change with my money, or with the world and the code?**

Money → **elgar** (private). World/code → **`.fux`** (public). Nothing lives in a home-directory pack or a loose file. This test is the root the money/knowledge mandates below descend from.

---

## The six apex rules

| Rule | Seals (Anton-enforceable) | Cited as fact (not sealed) | Lever / code |
|------|---------------------------|----------------------------|--------------|
| **plan-store** | Money docs (`*.plan.md`/`*.drift.md`) + hard PII (PAN/Aadhaar/account-ids) never enter this public repo | worked-example ₹ figures stay WARN | `dante pii` + `fux gate` CI |
| **configurable-paths** | No hardcoded path; every dir derives from one env base `ANTON_DATA_DIR`, individually overridable | — | `app.core.paths` |
| **elgar-mandate** | Elgar is the money home; public repos hold `elgar://plan/<id>` links only; Anton owns no elgar path, reaches it only via the elgar CLI, fail-loud | git/0700/one-commit storage mechanics; default store shares the elgar source repo's `.git` (only as private as that repo) | `elgar_bridge.py`, `plan_loader.py`, `elgar-store-guard` probe |
| **fux-mandate** | Anton's knowledge layer is Fux, pinned to a `$0`/deterministic/no-mandatory-LLM version; bumps that weaken that are rejected | the no-LLM guarantee is owned + enforced by fux's own guard test | the exact version pin (`pyproject.toml`) |
| **bach-mandate** | Bach is the single secrets home; no secret in VCS or the tree; Anton reads secrets only via token-scoped `vault_client` | Argon2 KDF + 127.0.0.1 bind (bach-owned, upgradeable); the file-env path is a shrinking migration fallback | `vault_client.py`, `broker_env.py` |
| **wagner-mandate** | Anton owns no auth logic; `/iam/*` is a transparent proxy to Wagner; the removed IAM tables must never return | Wagner's RBAC, token rotation/reuse-detection, API keys, audit log | `iam_proxy.py`, `config.py`, `remove_iam_tables` migration |

---

### plan-store — money & PII never enter the public repo *(first constitutional rule, ratified 2026-06-17)*

Personal financial documents and hard identifiers (PAN, Aadhaar, broker account/client/folio numbers) must never be committed to Anton, including `.fux/`. Two always-blocking classes matched to the `dante pii` BLOCK tier; plans live in elgar, the repo holds `elgar://plan/<id>` links. Worked-example ₹ amounts are WARN (`pii:allow` whitelists a line). Enforced by `dante pii` + `just probe plan-safety` at pre-commit **and** the required `just constitution` (`fux gate`) CI check.

### configurable-paths — one env-driven base

No hardcoded filesystem path. Every directory the app reads or writes resolves through `app.core.paths`, derives from `ANTON_DATA_DIR`, is individually overridable, and is documented in `.env`. Never `Path.home()` or a `~/.alphaforge-anton/...` literal inline.

### elgar-mandate — the private money store

Elgar is the canonical home for money knowledge; public repos hold links, never content. **Delegation:** Anton holds no elgar filesystem path — it reaches the store only through the elgar CLI API (`elgar_bridge`), fail-loud (`ElgarStoreError`, never a silent local fallback); `ELGAR_DIR` is configured on the elgar side, a deliberate exception to `configurable-paths` because the store is externally owned. **Honest correction:** the default store is a `store/` collection *inside* the elgar source repo sharing its `.git` — it is only as private as that repo; it is *not* "outside any public tree" by default. (The standard ADR `anton-delegates-elgar-store` was merged into this rule on 2026-06-28.)

### fux-mandate — the knowledge engine

Anton's knowledge layer is Fux: code-bound rules recording *why* the code is the way it is, read before any edit, warned on drift. Anton must stay pinned to a Fux version whose maintenance/derive/check path is `$0`, deterministic, stdlib-only, with no mandatory LLM call. That guarantee is **owned upstream** by fux's own guard test; Anton's enforceable lever is the **exact version pin** — a bump that introduces a mandatory model call is rejected at review.

### bach-mandate — the secrets vault

Bach is the single home for every secret (broker creds, LLM keys, wagner's `JWT_SECRET`/`DATABASE_URL`), under a namespaced app token, never committed to VCS or left in the tree. Anton reads secrets only via token-scoped `vault_client.load_from_vault`. Bach's Argon2 KDF and 127.0.0.1 bind are bach-owned facts (a KDF upgrade is legitimate, so not sealed). The file-env path in `vault_client.py` is a documented, shrinking migration fallback, not a second secret home. `vault-only-credentials` is the broker-credential instance of this charter.

### wagner-mandate — identity & access, delegated

Anton owns no authentication or authorization logic. Every `/iam/*` request is forwarded by `iam_proxy` to Wagner as a transparent proxy; the IAM tables Anton once held and removed must never return. **Carve-outs that keep it true:** local *stateless* token verification (JWKS signature check/cache) is allowed but never the source of truth; the proxy's logout `401→204` rewrite is presentation-only, never an authorization decision. Wagner's RBAC, token rotation, API keys, and audit log are Wagner-owned facts, not sealed here.

---

## Why plan-store and elgar-mandate stay separate

A recurring question is whether `plan-store` should be folded into `elgar-mandate` (or `fux-mandate`). It deliberately stays its own rule, for the same reason the `elgar-mandate` debate split them in the first place:

- **`plan-store` is the wall — the deterministic gate.** It binds exactly what `dante pii` can BLOCK and `fux gate` can enforce in CI. Its whole value is that a violation is *mechanically* caught, not reviewed. That is the part the apex can actually keep.
- **`elgar-mandate` is the charter — the affirmative "what elgar is for."** It names elgar the money home, the two-place placement law, and the delegation invariant. Much of it (storage mechanics, the elgar CLI) is cited as fact, not deterministically gated.

Folding the wall into the charter would (a) require **superseding** committed law (plan-store predates this session and is sealed), (b) re-point the **14 rules** that link `[[plan-store]]` plus the `CLAUDE.md`/docs/`justfile`/`constitution.yml` references to it, and (c) blur a clean separation — gate vs charter — for no enforcement gain. `fux-mandate` is the wrong home entirely: it governs the knowledge engine, not money or PII. So the wall stays standalone, and `elgar-mandate` references it as `its wall`. One invariant, one home — the duplication the debates warned against is avoided.

## Amendment

A constitutional rule governs its own amendment. None of the six can be changed in place: the only lawful path is **supersede + re-ratify** through `/fux debate` and `fux ratify`, which re-stamps the lock. This document is a derived view and may be edited freely — it carries no seal.

*Authoritative status: `fux constitution`. Per-rule text: `fux why <id>`. Debate record: `.fux/debates/<id>.md`.*
