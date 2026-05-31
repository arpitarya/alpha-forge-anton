# AlphaForge Anton — Commands

```bash
# ── Local development (all services) ────────────────────────────────────────
./start.sh                # Start PostgreSQL, Redis, Bach vault, backend, frontend
./stop.sh                 # Stop all services started by start.sh

# ── Full repo setup ───────────────────────────────────────────────────────────
./setup.sh                # One command to set up everything
./setup.sh --help         # Show all setup.sh options

# ── Setup — granular ─────────────────────────────────────────────────────────
./setup.sh --prereqs      # Check/install pyenv, nvm, pnpm, uv
./setup.sh --venv         # Create .venv via `uv venv` (reads .python-version)
./setup.sh --backend      # Sync the entire Python workspace (uv sync)
./setup.sh --frontend     # Frontend + workspace deps (pnpm) + build ravel-ui
./setup.sh --env          # Scaffold .env files from examples
./setup.sh --dirs         # Create log/data/model directories
./setup.sh --db           # Setup local PostgreSQL + Redis (macOS Homebrew)

# ── Python Workspace (uv) ────────────────────────────────────────────────────
uv sync                              # Install/refresh every workspace member into .venv
uv lock                              # Refresh uv.lock without installing
uv add httpx --package alphaforge-anton-backend   # Add a dep to a specific member
just sync                            # Same as `uv sync` (justfile shortcut)

# ── Backend ──────────────────────────────────────────────────────────────────
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd backend && uv run pytest -v
uv run ruff check .

# ── Backend Debugging (VS Code) ──────────────────────────────────────────────
# Option A — launch directly: pick "Backend: FastAPI (uvicorn, debug)" in Run & Debug (F5)
# Option B — attach to running process:
just backend-debug                   # Starts uvicorn under debugpy (waits on :5678)
                                     # Then pick "Backend: Attach (debugpy on :5678)" in VS Code
# Option C — debug current pytest file: open a test file → "Backend: Pytest (current file)"

# ── Frontend ─────────────────────────────────────────────────────────────────
cd frontend && pnpm dev              # Dev server
cd frontend && pnpm lint             # Lint
cd frontend && pnpm type-check       # TypeScript check

# ── UI Package ───────────────────────────────────────────────────────────────
cd packages/ravel-ui && pnpm build   # Build ESM + CJS + DTS
cd packages/ravel-ui && pnpm dev     # Watch mode

# ── Infrastructure ───────────────────────────────────────────────────────────
./setup.sh --db                                                  # macOS native (Homebrew)
# OR:
docker compose -f infra/docker-compose.yml up -d                 # via OrbStack

# ── Migrations ───────────────────────────────────────────────────────────────
cd backend && uv run alembic upgrade head
cd backend && uv run alembic revision --autogenerate -m "description"

# ── Probes (UI + Broker verification) ────────────────────────────────────────
# Probes attach to the existing Chrome session via CDP (:9299) — never use Playwright MCP.
# See probes/WHY_PROBES_NOT_MCP.md for the rationale.

just zerodha-chrome          # Open Chrome with CDP on :9299 (required by all UI probes)

# UI probes — full-stack verification via CDP
just ui-probe                # Full UI smoke test: auth, dashboard, portfolio, console errors
just ui-portfolio            # Portfolio filter probe: chips, sort, PnL filter, text search
just ui-screens              # Capture terminal / portfolio / preferences screenshots
just ui-pref-tabs            # Walk every Preferences sidebar tab → screenshots
just ui-concierge            # Concierge AI chat UI probe
just ui-model-picker         # Model picker UI probe

# Or run directly:
uv run python probes/ui_probe.py
uv run python probes/ui_portfolio_probe.py
uv run python probes/ui_screens.py

# Broker XHR probes — confirm live API endpoints match source code
just probe-zerodha           # Zerodha equity holdings (enctoken)
just probe-zerodha-coin      # Zerodha Coin MF holdings (enctoken)
just probe-zerodha-cash      # Zerodha free cash
just probe-groww             # Groww equity holdings (XHR intercept)
just probe-groww-cash        # Groww free cash
just probe-angelone          # Angel One holdings (XHR intercept)
just probe-angelone-cash     # Angel One free cash
just probe-indmoney          # IndMoney US holdings (XHR intercept)
just probe-indmoney-cash     # IndMoney free cash
just probe-binance           # Binance crypto wallet (XHR intercept)
just probe-binance-cash      # Binance free cash
just probe-tickertape        # Ticker Tape portfolio (XHR intercept)
just probe-gullak            # Gullak gold holdings

# ── Repo Context MCP ─────────────────────────────────────────────────────────
# (code-search server for Claude/Copilot/Cursor — separate from UI probes)
cd repo-context-mcp && pdm install                               # Install deps
cd repo-context-mcp && pdm run index --full                      # Build initial vector index
cd repo-context-mcp && pdm run index --watch                     # Watch + incremental reindex
cd repo-context-mcp && pdm run serve                             # Run MCP server (stdio)
alphaforge-anton-repo-context-mcp                                      # Same server (after `pdm install`)

# ── Cleanup ──────────────────────────────────────────────────────────────────
./clean.sh                # Remove build artifacts and bytecode (keeps venv + node_modules)
./clean.sh --cache        # Remove only tool caches
./clean.sh --venv         # Remove Python venv
./clean.sh --backend      # Deep-clean backend (artifacts, caches, venv)
./clean.sh --frontend     # Deep-clean frontend (.next, node_modules)
./clean.sh --all          # Nuclear clean — removes everything (run setup.sh to restore)
```
