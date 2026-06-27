# CLAUDE.md — Context for Claude Code

**AlphaForge Anton** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Python 3.14/FastAPI backend + Next.js 15/TypeScript frontend monorepo. Self-hosted, MIT licensed.

## Docs Index

| Topic | File |
|-------|------|
| Architecture, repo tree, tech decisions, key files | [docs/architecture.md](docs/architecture.md) |
| Coding conventions (Python + TypeScript) | [docs/conventions.md](docs/conventions.md) |
| CLI commands (setup, run, build, migrate, clean) | [docs/commands.md](docs/commands.md) |
| Guardrails & project rules | [docs/guardrails.md](docs/guardrails.md) |
| Runtime money/PII critic (Orff live-write guard) | [docs/runtime-critic.md](docs/runtime-critic.md) |
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) |
| Signals engine (deterministic swing verdicts) | [docs/signals.md](docs/signals.md) |
| Edge-discovery engine (pre-registered hypotheses, gates 0–2 + journal + trial-ledger + null-data) | [docs/edges.md](docs/edges.md) |
| Phase-0 contracts (engine↔UI shapes + TS codegen) | [docs/contracts.md](docs/contracts.md) |
| Comparison docs — how to write `<name>.compare.md` | [docs/comparison.guide.md](docs/comparison.guide.md) |
| Graphify knowledge graph | [docs/graphify.md](docs/graphify.md) |
| Cage LLM cost ledger (Orff integration) | [docs/cage.md](docs/cage.md) |
| Vault-backed secrets (alpha-forge-bach) | [docs/vault.md](docs/vault.md) |
| Orff concierge AI implementation docs | [concierge/README.md](concierge/README.md) |
| Probes — how to write & run CDP verification probes | [probes/Probes.md](probes/Probes.md) |

## Must-Know Rules

Apply these on every file without looking up the docs:

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Backend filenames: `{domain}_{role}.py` — Frontend: `{domain}.{role}.ts`
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff (line-length=100)
- TypeScript: strict mode, functional components only, pnpm, Biome v2
- Never commit `.env` files or API keys
- **[CONSTITUTIONAL]** Never commit money docs (`*.plan.md` / `*.drift.md`) or hard PII (PAN / Aadhaar / broker account-client-folio numbers) — money docs live in the private **elgar** store (`elgar save <id>`); this repo holds `elgar://plan/<id>` links only. Worked-example ₹ figures are allowed (WARN; `pii:allow` to whitelist a line). This is `plan-store`, anton's **first constitutional rule** (sealed in `.fux/constitution.lock`); it cannot change in place — supersede + re-ratify. Enforced by `dante pii` + `just probe plan-safety` via pre-commit **and** the required `just constitution` (`fux gate`) CI check — `fux why plan-store`
- **Runtime money/PII guard** — at runtime, Orff writes to the elgar store from free text where no commit hook runs. The `runtime-note-pii` principle guards the one riskiest live path (`append_memory`): `critic_guard.review_note` BLOCKs the same PAN/Aadhaar/account patterns as `dante pii` **before** the write (→ HTTP 422). The judgment layer (`fux critic`) is advisory-first. Scoped to `append_memory` only — do not widen without review. `fux why runtime-note-pii` · `just probe critic-runtime` · [docs/runtime-critic.md](docs/runtime-critic.md)
- All broker CSV dumps use `dump_utils.py` — see [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md)
- Every code change must be accompanied by a doc update in the same session
- **UI & broker verification: always use `probes/` (CDP :9299), never Playwright MCP** — see [probes/WHY_PROBES_NOT_MCP.md](probes/WHY_PROBES_NOT_MCP.md). New features need a probe + `just` recipe before they count as verified.

## Skills

| Trigger | What it does |
|---------|--------------|
| `/broker` | Add, edit, or remove a broker source (registry, module files, fixtures, docs) |

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files. Run them **metered through cage**: bare `graphify …` is auto-metered once the `bin/graphify` shim is on PATH (after `setup.sh --graphify`), or call it explicitly with `cage graphify -- graphify query "…"` / `just graphify-cage 'query "…"'`. This files a `tool="graphify"` token-saving receipt (`cage matrix` graphify×fux).
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost). Leave `graphify update .` **unwrapped** — it's a refresh, not a query, so there's nothing to meter.

<!-- fux:start -->
## Fux knowledge engine

This project's rules, memory, narrative, and graph live in `.fux/` (one substrate). **SessionStart auto-injects the INDEX** — no manual setup needed.

### Core commands

| Command | Purpose |
|---------|---------|
| `fux why <id>` | Retrieve a rule's decision, context, and code refs — use before answering "why" questions |
| `fux refs <path>` | See which rules & ADRs govern a file — start here when modifying code |
| `fux check` | Verify no drift between config + rules + code — run before distilling |
| `fux build` | Rebuild INDEX + derived views ($0, AST-only) — run after manual edits to `.fux/` |
| `/fux distill "<focus>"` | Capture this session's durable decisions → `memory` / `adr` entries (user-confirmed) |

### Copilot hooks (auto-enabled)

1. **SessionStart** — `.fux/out/INDEX.md` injected; skim if session modifies ruled files  
2. **UserPromptSubmit** — `fux hook-recall` injects only the rules relevant to the prompt  
3. **Pre-answer** — On questions about architecture, decisions, or file governance, call `fux why <id>` or `fux refs <path>` first  
4. **SessionEnd** — Consider `/fux distill` to convert session insights into version-controlled knowledge (only user-confirmed writes)  

### When to reach for Fux

- ✅ "Why does the code do X?" — `fux why <rule-id>` (captures intent + consequences)  
- ✅ "What governs my changes to file Y?" — `fux refs <path>` (avoids breakage)  
- ✅ "How do modules A and B relate?" — `fux explain "<concept>"` (traverses EXTRACTED + INFERRED edges)  
- ✅ "I need to capture this session's decision" — `/fux distill` (durable, code-linked, searchable)  
- ❌ "Find all imports of X" — use grep (faster, one-off)  
- ❌ "Show me the code in file Y" — use semantic search (returns full context)  

### Distillation workflow

At session end, if you made non-obvious decisions:
1. Run `/fux distill` → lists candidates (memory / adr / rule)  
2. **Confirm or trim** — user decides what's durable  
3. **Author** — each confirmed entry gets `type`, `id`, `scope`, `code_refs`  
4. **Link** — add `edges:` to neighbouring entries so knowledge joins the graph  
5. **Verify** — `fux build && fux check` before closing session  

**Guardrail:** A distilled entry must be reusable next month — skip transient debugging steps, one-off file paths, or facts already in rules.
<!-- fux:end -->

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

<!-- cage:start -->
## Cage — LLM cost & savings ledger

This project meters LLM traffic into `.cage/` (a *flux*: $0, deterministic).

- Spend so far: `cage report` · per-tool savings: `cage attrib` · budget: `cage budget`
- The ledger carries token *counts*, never prompt text — PII-safe by construction.
- Edit prices / budgets / pipeline order in `.cage/policy.toml`.
<!-- cage:end -->
