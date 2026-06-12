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
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) |
| Comparison docs — how to write `<name>.compare.md` | [docs/comparison.guide.md](docs/comparison.guide.md) |
| Graphify knowledge graph | [docs/graphify.md](docs/graphify.md) |
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
- Never commit money docs (`*.plan.md` / personal figures) — they live in the private **elgar** store (`elgar save <id>`); this repo holds `elgar://plan/<id>` links only. Enforced by `just dante-pii` + pre-commit — `fux why plan-store`
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
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

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
