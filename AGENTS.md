# AGENTS.md — Context for OpenAI / Codex Agents

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
| Graphify knowledge graph | [docs/graphify.md](docs/graphify.md) |

## UI & Broker Verification

**Always use probes (`probes/`), never Playwright MCP**, for any UI or broker endpoint verification.

Probes are Python scripts that attach to the existing AlphaForge Chrome via CDP on port 9299 — the same session used by broker scrapers. They have full access to project internals, run without Claude, and are version-controlled.

| Probe | Command | Purpose |
|-------|---------|---------|
| `ui_probe.py` | `just ui-probe` | Full auth + dashboard + portfolio smoke test |
| `ui_portfolio_probe.py` | `just ui-portfolio` | Portfolio filter chips, sort, PnL filter, text search |
| `ui_screens.py` | `just ui-screens` | Terminal / portfolio / preferences screenshots |
| `ui_pref_tabs.py` | `just ui-pref-tabs` | Preferences sidebar tab screenshots |
| `ui_concierge_probe.py` | `just ui-concierge` | Concierge AI chat UI |
| `ui_model_picker_probe.py` | `just ui-model-picker` | Model picker UI |
| `{broker}_probe.py` | `just probe-{broker}` | Broker XHR endpoint verification |

See [probes/WHY_PROBES_NOT_MCP.md](probes/WHY_PROBES_NOT_MCP.md) for the full rationale. When adding a new feature or broker, create a probe and a `just` recipe before marking it verified.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
