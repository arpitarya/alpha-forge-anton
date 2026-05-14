# CLAUDE.md — Context for Claude Code

**AlphaForge** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Python 3.14/FastAPI backend + Next.js 15/TypeScript frontend monorepo. Self-hosted, MIT licensed.

## Docs Index

| Topic | File |
|-------|------|
| Architecture, repo tree, tech decisions, key files | [docs/architecture.md](docs/architecture.md) |
| Coding conventions (Python + TypeScript) | [docs/conventions.md](docs/conventions.md) |
| CLI commands (setup, run, build, migrate, clean) | [docs/commands.md](docs/commands.md) |
| Guardrails & project rules | [docs/guardrails.md](docs/guardrails.md) |
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) |
| Graphify knowledge graph | [docs/graphify.md](docs/graphify.md) |

## Must-Know Rules

Apply these on every file without looking up the docs:

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Backend filenames: `{domain}_{role}.py` — Frontend: `{domain}.{role}.ts`
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff (line-length=100)
- TypeScript: strict mode, functional components only, pnpm, Biome v2
- All AI outputs include financial disclaimer
- Never commit `.env` files or API keys
- All broker CSV dumps use `dump_utils.py` — see [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md)
- Every code change must be accompanied by a doc update in the same session
