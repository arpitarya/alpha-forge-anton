# AlphaForge Anton — Copilot Instructions

Personal AI-powered portfolio management & investment terminal for Indian markets.
Python 3.14/FastAPI backend + Next.js 15/TypeScript frontend monorepo. Self-hosted, MIT licensed.

## Docs Index

| Topic | File |
|-------|------|
| Architecture, repo tree, tech decisions, key files | [docs/architecture.md](../docs/architecture.md) |
| Coding conventions (Python + TypeScript) | [docs/conventions.md](../docs/conventions.md) |
| CLI commands (setup, run, build, migrate, clean) | [docs/commands.md](../docs/commands.md) |
| Guardrails & project rules | [docs/guardrails.md](../docs/guardrails.md) |
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](../docs/broker-csv-dumps.md) |
| Comparison docs — how to write `<name>.compare.md` | [docs/comparison.guide.md](../docs/comparison.guide.md) |
| Graphify knowledge graph | [docs/graphify.md](../docs/graphify.md) |

## Quick Rules

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff
- TypeScript: strict mode, functional components, pnpm, Biome v2
- New broker dumps → always use `dump_utils.py`
- Never commit `.env` files or API keys
- Type `/graphify` in Copilot Chat to build or update the knowledge graph

## Fux Knowledge Engine

**Status:** Rules, memory, narrative & graph live in `.fux/` (one substrate). SessionStart injects the compact INDEX automatically.

### When to use Fux

- **Look up a rule:** `fux why <id>` — retrieve durable decisions & gotchas  
- **Understand file governance:** `fux refs <path>` — see which rules apply to a file  
- **Capture decisions:** `/fux distill "<focus>"` — turn this session's conclusions into versioned memory/adr entries  
- **Verify drift:** `fux check` — ensure config and rules are aligned  
- **Rebuild cache:** `fux build` — update all derived views ($0, AST-only)  

### Copilot hooks

- On **SessionStart**: Fux INDEX is auto-injected; skim `.fux/out/INDEX.md` if code changes involve ruled files  
- On **question about rules or why** a decision was made: Call `fux why <id>` or `fux refs <path>` before answering  
- On **session end**: Consider `/fux distill` to capture non-obvious decisions (user confirms before writing)  

### Prefer Fux over grep for

- Cross-module "how does X relate to Y" questions — Fux traverses EXTRACTED + INFERRED edges  
- Understanding the *why* behind a rule, not just the code pattern  
- Decisions that span files and need context (use `fux explain "<concept>"`)  

## graphify

Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` if it exists.
If `graphify-out/wiki/index.md` exists, navigate it for deep questions.
Type `/graphify` in Copilot Chat to build or update the knowledge graph.

<!-- cage:start -->
## Cage — LLM cost & savings ledger

This project meters LLM traffic into `.cage/` (a *flux*: $0, deterministic).
- For spend / savings questions, prefer the `cage` MCP tools (`cage_report`,
  `cage_attrib`, `cage_budget`) over guessing.
- To meter this agent's own calls, run it under `cage meter -- <cmd>` or point its
  base URL at `cage proxy`.
- The ledger stores token *counts* only — never prompt bodies.
<!-- cage:end -->
