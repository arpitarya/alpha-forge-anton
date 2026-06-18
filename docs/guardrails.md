# AlphaForge Anton — Guardrails

## Security

- Never commit `.env` files or API keys — add new vars to the appropriate `.env.example` instead
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only; allowed methods/headers are explicit (not `*`)
- No guaranteed return claims anywhere in code or UI
- All financial amounts use `float` for now (will migrate to `Decimal` before production)
- Password hashing uses `bcrypt` directly (passlib removed — incompatible with bcrypt 4.x)
- Auth enforced via `Depends(get_current_user)` on all routes except `/health` and `/auth/token`
- Auth handled by Wagner IAM — user credentials managed in Wagner's database; probe credentials stored in afbach vault as `PROBE_USER` / `PROBE_PASS`
- Cloud LLM providers disabled in `APP_ENV=development` unless `ALLOW_CLOUD_LLM_IN_DEV=true`
- Broker outbound HTTP guarded against unapproved hosts in dev mode via `BROKER_ALLOWED_HOSTS`
- Run `just audit` to scan Python + Node dependencies for known CVEs
- **[CONSTITUTIONAL] Money documents & hard PII never live in this repo.** This is `plan-store`, anton's first **constitutional** Fux rule — ratified, content-sealed in `.fux/constitution.lock`, and gate-enforced; it cannot change in place (supersede + re-ratify only). Two always-blocking classes, matched to the `dante pii` BLOCK tier:
  - **Money documents** — `*.plan.md` / `*.drift.md` and any saved plan, strategy plan (targets/bands/rules), projection, or saved Orff plan conversation. These live only in the private elgar store (`elgar save <id>`, default `~/.alphaforge-anton/elgar`); commit only `elgar://plan/<id>` links. (CRITICAL → BLOCK.)
  - **Hard identifiers** — PAN, Aadhaar, broker account / client / folio numbers. (HIGH → BLOCK.)

  Worked-example ₹ amounts in docs / knowledge rules / eval fixtures are permitted (MEDIUM → WARN); whitelist an intentional line with `pii:allow`. Real position figures stay out via the money-doc class above + `context-docs-figure-free`.
  **Enforcement (two layers):** `dante pii` (`DANTE_ENFORCE=true`) + `just probe plan-safety` in the pre-commit hook — *bypassable with `--no-verify`* — **and** the **required** `just constitution` (`fux gate`) CI check, which is the wall (`fux gate` exits 2 on any constitutional finding). See `fux why plan-store`.
- **Runtime money/PII guard — the live-write twin of `plan-store`.** `plan-store` blocks money/PII at the **commit** boundary; the Orff agent also writes to the elgar store **at runtime** (free agent/user text), where no pre-commit hook runs. The `runtime-note-pii` principle (`fux why runtime-note-pii`) closes that hole on the one riskiest path: `append_memory` (the `orff-context` note). `critic_guard.review_note` runs the **same** PAN / Aadhaar / account-number BLOCK patterns as `dante pii`, **before** the elgar save — a match raises `ForbiddenRuntimeAction` (HTTP 422) and nothing is written. This is a `deterministic` principle and **always blocks** (it is not an opinion). A second, **advisory** layer (`fux critic`, advisory-first since fux ≥ 0.5.0) surfaces money/PII *judgment* concerns for host-agent self-critique without blocking; Cage meters any tokens it spends. **Scope:** `append_memory` only — `set_objective` / `save_action_plan` are deliberately not yet guarded; widening is a separate reviewed step. Verified by `just probe critic-runtime`.

## The constitution wall — branch protection (watched, not sealed)

- **The required CI checks are the wall; branch protection makes them binding.** `main` requires two status checks before any merge: **`gate`** (`fux gate` — constitution integrity, exit 2 blocks) and **`ai-review`** (a separate-reviewer constitutional second pass that REFUSES, exit 3, when reviewer == PR author — separation of duties, §2R). Both are required in `.github/branch-protection.json` by their **bare job names** (the strings the check-runs API reports — *not* `constitution / gate`). Local pre-commit is bypassable with `--no-verify`; these required checks are not.
- **No direct path to `main`.** `enforce_admins: true` + no force-push + no deletion means *no one* — including the owner — can push, force-push, or delete `main`. Every change goes through a new branch → PR → green `gate` + `ai-review` → merge. `required_pull_request_reviews` is `null` on purpose (solo dev — review is enforced as *checks*, not an approval click; restore a review count only if a second maintainer joins).
- **Branch protection is GitHub config Fux CANNOT seal** (handoff §1) — `constitution.lock` covers rules/code, never the GitHub setting. So the setting is **watched, not sealed:** the committed `.github/branch-protection.json` is the source of truth, `scripts/apply-branch-protection.sh` re-applies it in one command, and a **weekly drift audit** (`.github/workflows/audit-protection.yml` + `just audit-protection`) asserts both required contexts + `enforce_admins=true` and **fails loudly** on any drift vs the committed JSON. The CI audit needs an admin-scoped `BRANCH_PROTECTION_TOKEN` secret (the default `GITHUB_TOKEN` cannot read protection) and exits non-zero rather than passing silently if it cannot read.
- **Constitutional amendments route through the gate by construction.** `fux ratify` / `/fux debate` (fux-engine ≥ 0.6.0) open a `constitution/<id>` branch and a PR automatically instead of committing to `main` (`--no-pr` only for local/offline) — a ratification physically cannot land except through the gated PR (§2g).
- **Agent authorship is auditable.** Claude Code commits under a distinct git identity (`Claude (agent) <claude-code@anton.local>`, set by `scripts/git-identity-claude.sh`) with an `Agent: claude-code` trailer (`.gitmessage-claude`). No new GitHub account — a dedicated bot/GitHub-App identity is deferred (§2R.4) until a forced approval click or a second agent is actually needed. See `docs/constitution-enforcement-handoff.md` (in the fux repo) for the full rationale.

## Documentation

- Every code change must be accompanied by a documentation update in the same session
- Detailed project docs in `docs/`: WHY.md (vision), WHAT.md (features), HOW.md (architecture), GETTING_STARTED.md (setup)

## Planning

- When planning a new module or feature, create a `PLAN.md` inside that module's directory with the full plan, goals, phases, and design decisions; then link it from the root-level `PLAN.md` so all plans can be tracked from one place

## Implementation Tracking

- When a new module or feature is built, create an `implement.txt` inside that module's directory logging what was built, decisions made, and status; then link it from the root-level `implement.txt` so all modules can be tracked from one place

## File Layout

- Follow naming rules in [structure/README.md](../structure/README.md). Each top-level module has its own `files.md` and `variables.md`; consult them before creating a new file or naming a new symbol
- Files ≤ 100 lines (≤ 50 for `*_utils.py` / `*.utils.ts`) — see [conventions.md](conventions.md)

## Environment Variables

- All ports defined in `.env.port` at repo root
- Add new vars to the appropriate `.env.example` file — never commit `.env`
- **Broker user IDs and API keys must live in the afbach vault, never in `.env` files** — vault-only keys are not listed in `.env.cred.example`
- Vault-aware env helpers are in `broker_env.py`: use `source_ready(REQUIRED_ENV, env)` in source `__init__` and `require_env(key, env)` in acquire functions — both surface a `vault locked` hint automatically

## UI Verification

- **Always use probes (`probes/`) for all UI and broker verification — never Playwright MCP**
- Probes attach to the existing Chrome session via CDP (port 9299) — the same session the broker scrapers already use. No extra browser setup required.
- Each probe is a Python script checked into the repo, runnable independently of Claude: `just ui-probe`, `just ui-portfolio`, `just probe-zerodha`, etc.
- See [probes/WHY_PROBES_NOT_MCP.md](../probes/WHY_PROBES_NOT_MCP.md) for the full rationale.
- When adding a new UI feature or broker, add a corresponding probe in `probes/` and a `just` recipe in the justfile before considering the feature verified.
- Playwright MCP is acceptable only for ad-hoc one-off exploration of external third-party pages where no project internals are needed.

## Broker CSV Dumps

- All broker holdings dumps must use `dump_utils.py` — see [broker-csv-dumps.md](broker-csv-dumps.md)
