## justfile — common development commands

# Load port numbers from .env.port (BACKEND_PORT, FRONTEND_PORT, ...)
set dotenv-load := true
set dotenv-filename := ".env.port"

venv  := ".venv"
python := venv / "bin/python"

# Show this help
default:
    @just --list

# ── Setup ────────────────────────────────────────

# Ensure repo-level Python venv exists
venv:
    bash setup.sh --venv

# Full repo setup (prereqs, venv, all deps, env files, dirs)
setup:
    bash setup.sh
    @echo "✅ Setup complete"

# Check/install system prerequisites (pyenv, nvm, pnpm, uv)
setup-prereqs:
    bash setup.sh --prereqs

# Scaffold .env files from .env.example templates (non-destructive)
setup-env:
    bash setup.sh --env

# Sync .env files from .env.example templates + auto-generate blank secrets (idempotent)
setup-config:
    bash setup-config.sh

# Preview what setup-config would change without writing
setup-config-check:
    bash setup-config.sh --check

# Sync env keys only — skip secret auto-generation
setup-config-keys:
    bash setup-config.sh --no-secrets

# Create all required directories (logs, screener data, models)
setup-dirs:
    bash setup.sh --dirs

# Setup graphify for Claude, Codex, Copilot, git hooks, and graph output
graphify-setup:
    bash setup.sh --graphify

# Refresh graphify-out after code changes
graphify-update:
    graphify update .

# Check whether graphify needs a semantic refresh
graphify-check:
    graphify check-update .

# Backfill one human-baseline (Tier-1) receipt per task → feeds `cage human` / `cage trend`
cage-human:
    uv run --project concierge/llm --extra cage python -m alphaforge_anton_llm.cage_human

# Run a graphify query metered through cage: just graphify-cage 'query "how does X relate to Y"'
graphify-cage args:
    cage graphify -- graphify {{args}}

# ── Full Stack ───────────────────────────────────

# Start all local services: DB, Bach vault, backend, frontend
start:
    bash start.sh

# Stop all local services started by start.sh
stop:
    bash stop.sh

# Start backend + frontend via Procfile (requires DB running)
dev-local:
    #!/usr/bin/env bash
    if command -v overmind >/dev/null 2>&1; then
        overmind start
    elif command -v honcho >/dev/null 2>&1; then
        honcho start
    else
        echo "❌ Install overmind (brew install overmind) or honcho (pip install honcho)"
        exit 1
    fi

# Start all services with Docker/OrbStack
dev-docker:
    docker compose --env-file .env.port -f infra/docker-compose.yml up --build

# Stop Docker services
down:
    docker compose --env-file .env.port -f infra/docker-compose.yml down

# ── Backend ──────────────────────────────────────

# Run backend dev server
backend:
    cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT}

# Run backend under debugpy (VS Code attaches via "Backend: Attach (debugpy on :5678)")
backend-debug port="5678":
    @echo "🐛 Backend waiting for debugger on 127.0.0.1:{{port}} — attach in VS Code"
    cd backend && uv run python -m debugpy --listen 127.0.0.1:{{port}} --wait-for-client \
        -m uvicorn app.main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT}

# Install backend Python dependencies (alias — `just sync` is the primary entry point now)
backend-install:
    bash setup.sh --backend

# ── Frontend ─────────────────────────────────────

# Run frontend dev server
frontend:
    cd frontend && pnpm dev

# Install frontend Node dependencies
frontend-install:
    bash setup.sh --frontend

# ── LLM ──────────────────────────────────────────

# Run the standalone LLM provider playground (http://localhost:${LLM_PLAYGROUND_PORT})
llm:
    -lsof -ti :${LLM_PLAYGROUND_PORT} | xargs kill -9 2>/dev/null || true
    cd llm && uv run uvicorn playground.server:app --host 127.0.0.1 --port ${LLM_PLAYGROUND_PORT} --reload

# ── Concierge ────────────────────────────────────

# Regenerate the frontend registry from the manifest (concierge/llm/.../registry/*.json)
gen-concierge:
    cd frontend && pnpm gen:concierge

# Verify the committed generated registry is in sync with the manifest (CI guard)
gen-concierge-check:
    cd frontend && pnpm gen:concierge:check

# Sync investment-related Claude Code chats into Orff history (elgar sessions/).
# Re-runnable & idempotent. Preview first: just sync-claude-history --dry-run
sync-claude-history *args:
    cd backend && uv run python -m app.modules.concierge.claude_import {{args}}

# ── Database / Infrastructure ────────────────────

# Setup PostgreSQL & Redis via Homebrew (macOS, no Docker)
db-local:
    bash setup.sh --db

# Start PostgreSQL & Redis (Homebrew)
db-start:
    bash database/db.sh start

# Stop PostgreSQL & Redis (Homebrew)
db-stop:
    bash database/db.sh stop

# Restart PostgreSQL & Redis (Homebrew)
db-restart:
    bash database/db.sh restart

# Show PostgreSQL & Redis status
db-status:
    bash database/db.sh status

# Start PostgreSQL & Redis via Docker/OrbStack
db-up:
    docker compose --env-file .env.port -f infra/docker-compose.yml up postgres redis -d

# Run Alembic migrations (upgrade head)
db-migrate:
    cd backend && uv run alembic upgrade head

# Create a new migration  (usage: just db-revision "add users table")
db-revision msg:
    cd backend && uv run alembic revision --autogenerate -m "{{msg}}"

# ── Signals ──────────────────────────────────────

# Backtest the active strategy.config over cached yfinance history (Phase 5, §10.5).
# Reports expectancy, win-rate, max drawdown & P&L AFTER costs — the go/no-go before sizing up.
backtest:
    cd backend && uv run python -m app.modules.signals.backtest_cli

# ── Edges ────────────────────────────────────────

# Run a PRE-REGISTERED edge hypothesis (elgar://edge/<id>) through gates 1-2 + journal.
# Reports per-gate expectancy / Calmar and the pass/kill verdict — see docs/edges.md.
edge id="":
    cd backend && uv run python -m app.modules.edges.edge_cli {{id}}

# Null-data trust check — feed RANDOM data through the funnel; assert it finds NO edge.
# A standing guard against fooling ourselves (overfit / look-ahead) — see docs/edges.md.
null-data:
    cd backend && uv run python -m app.modules.edges.null_selftest

# EB-0 — push pre-registered edge-001 through the funnel (Gates 1-3) on the committed offline
# panel and print a signed TestReport. PASS or honest KILL — never tuned. See docs/edges.md.
eb0:
    cd backend && uv run python -m app.modules.edges.eb0_cli

# EB-0 REAL — the base-rate verdict: edge-001's frozen campaign on the committed nse-bhavcopy panel
# (quality leg disabled-pending; per-rebalance liquidity). Journals the result to elgar — figures
# are NOT committed to this repo. Run `just ingest-nse` + `just build-panel` first. See docs/edges.md.
# Pass --exclusions <elgar-path> to apply the off-repo never-buy list.
eb0-real *ARGS:
    cd backend && uv run python -m app.modules.edges.eb0_real_cli {{ARGS}}

# ── Market-data ingestion (one-time, networked) ──

# One-time NSE EOD ingestion: pull cm-bhav + 2024+ UDiFF + NIFTY as raw zips into $NSE_DATA_DIR.
# PARALLEL (--workers N / NSE_WORKERS=8), resumable + self-healing (byte-integrity manifest), $0
# (stdlib urllib, never metered). Resume is manifest-based — a day already recorded (sha-matched)
# in cache-manifest.json is never re-downloaded, so re-run freely. For a big historical backfill,
# go polite-serial to avoid NSE throttling: NSE_WORKERS=2 NSE_REQUEST_DELAY=1.0 just ingest-nse ...
# --verify audits the cache offline; --quiet hides the progress bar; --raw-dir <dir> ingests
# pre-downloaded archives (no network). See docs/broker-csv-dumps.md.
ingest-nse FROM TO *ARGS:
    cd backend && uv run python -m app.modules.marketdata.bhavcopy_cli {{FROM}} {{TO}} {{ARGS}}

# Assemble the committed offline EB-0 panel from the bhavcopy cache (offline, $0, deterministic):
# build the per-rebalance liquidity superset, densify closes + turnover, run Gate-0, write the gzip
# panel. Pass --exclusions <elgar-path> to drop never-buy symbols. See docs/edges.md.
build-panel *ARGS:
    cd backend && uv run python -m app.modules.marketdata.panel_build {{ARGS}}

# ── Contracts ────────────────────────────────────

# Regenerate the frontend TS types from the Pydantic contract models ($0, deterministic).
# test_contracts_sync.py fails if the checked-in .ts drifts from these — see docs/contracts.md.
contracts-gen:
    cd backend && uv run python -m app.modules.contracts.contracts_codegen

# ── Probes ───────────────────────────────────────

# Run a probe by name — omit name to list all available probes (CDP :9299 required)
# Examples: just probe ui | just probe zerodha | just probe groww-cash
probe name="":
    bash probes/probe.sh {{name}}

# Regression guard — the deep-search confirm→apply loop closes in one turn (no re-arm)
deep-search-close:
    bash probes/probe.sh ui-deep-search-close

# ── Testing ──────────────────────────────────────

# Run all tests and linters
test: test-backend test-frontend

# Run backend tests (pytest)
test-backend:
    cd backend && uv run pytest -v --tb=short

# Run frontend lint + type-check (incl. registry-in-sync guard)
test-frontend:
    cd frontend && pnpm gen:concierge:check && pnpm lint && pnpm type-check

# ── Security ─────────────────────────────────────

# Audit Python + Node dependencies for known CVEs
audit:
    uv run pip-audit --desc
    cd frontend && pnpm audit --audit-level=high

# Dante: SAST + CVE + license audit (fast, local)
dante-audit:
    uv run dante audit --repo .

# Dante: personal-financial-info guard — money docs belong in the elgar store
# (also runs in the pre-commit hook with DANTE_ENFORCE=true)
dante-pii:
    DANTE_ENFORCE=true uv run dante pii --repo .

# Dante: full audit with JSON output (for CI / diff)
dante-audit-deep:
    uv run dante audit --repo . --json > .dante-audit.json

# Dante: apply hardening (writes public/robots.txt, etc.)
dante-harden:
    uv run dante harden --apply

# ── Quality ──────────────────────────────────────

# Lint everything
lint:
    uv run ruff format .
    cd frontend && pnpm lint

# ── Cleanup ──────────────────────────────────────

# Remove build artifacts and bytecode (keeps venv and node_modules)
clean:
    bash clean.sh

# Remove only tool caches
clean-cache:
    bash clean.sh --cache

# Remove the repo-level Python venv
clean-venv:
    bash clean.sh --venv

# Deep-clean backend — artifacts, caches, and venv
clean-backend:
    bash clean.sh --backend

# Deep-clean frontend — build output, cache, and node_modules
clean-frontend:
    bash clean.sh --frontend

# Nuclear clean — removes everything (run 'just setup' to restore)
clean-all:
    bash clean.sh --all

# ── Fux knowledge gate (plan §10.9) ───────────────────────────────
# Fail a PR on dead refs, schema errors, conflicts, or failed invariants.
fux-check:
    fux build
    fux check
    fux verify

# ── Constitution gate (REQUIRED CI check) ─────────────────────────
# The wall: `fux gate` exits 2 on any constitutional-tier finding — a tampered
# or unsealed apex rule (e.g. plan-store: money docs / hard PII). Local
# pre-commit is bypassable with --no-verify; this CI check is not.
constitution:
    fux gate

# ── Branch-protection drift audit (the second half of the wall) ───
# Branch protection is GitHub config Fux CANNOT seal (handoff §1) — so it is
# WATCHED, not sealed. Asserts the required checks (gate + ai-review) +
# enforce_admins=true are intact and that live protection matches the committed
# .github/branch-protection.json; FAILS LOUDLY on any drift. Also runs weekly in
# .github/workflows/audit-protection.yml. Needs gh with admin read on the repo.
audit-protection owner="arpitarya" repo="alpha-forge-anton" branch="main":
    ./scripts/audit-branch-protection.sh {{owner}} {{repo}} {{branch}}
