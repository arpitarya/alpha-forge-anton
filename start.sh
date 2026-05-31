#!/usr/bin/env bash
# start.sh — Start all Anton local development services + sister projects
# Services started:
#   PostgreSQL + Redis   (via database/db.sh)
#   Bach vault           (../bach)
#   Dante security API   (../dante, optional local HTTP API on :9100)
#   Wagner IAM backend   (../wagner, on :8001 to avoid clash with Anton :8000)
#   Anton backend        (FastAPI on :8000)
#   Anton frontend       (Next.js on :3000)
# Wagner + Dante code is also embedded inside Anton's backend; the standalone
# servers here are for direct development against those projects.
# Run ./stop.sh to stop everything.

set -euo pipefail

ANTON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRAMS_ROOT="$(cd "$ANTON_ROOT/.." && pwd)"
BACH_ROOT="$PROGRAMS_ROOT/bach"
DANTE_ROOT="$PROGRAMS_ROOT/dante"
WAGNER_ROOT="$PROGRAMS_ROOT/wagner"
PID_FILE="$ANTON_ROOT/.dev.pids"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BLUE='\033[0;34m'; MAGENTA='\033[0;35m'
PURPLE='\033[0;95m'; ORANGE='\033[0;33m'; NC='\033[0m'

log()  { echo -e "${CYAN}[start]${NC} $*"; }
ok()   { echo -e "${GREEN}[start]${NC} $*"; }
warn() { echo -e "${YELLOW}[start]${NC} $*"; }
err()  { echo -e "${RED}[start]${NC} $*" >&2; }

prefix_lines() {
    local col="$1" name="$2"
    while IFS= read -r line; do
        echo -e "${col}[${name}]${NC} ${line}"
    done
}

port_in_use() {
    lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -1 | grep -q .
}

free_port() {
    local name="$1" port="$2"
    port_in_use "$port" || return 0
    local pids
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | tr '\n' ' ' | sed 's/ $//')"
    warn "Port $port ($name) held by PID(s) $pids — killing…"
    # SIGTERM first
    for pid in $pids; do kill -TERM "$pid" 2>/dev/null || true; done
    local i=0
    while port_in_use "$port"; do
        i=$((i + 1))
        if [ "$i" -ge 5 ]; then
            # SIGKILL stragglers
            for pid in $pids; do kill -KILL "$pid" 2>/dev/null || true; done
            sleep 1
            break
        fi
        sleep 1
    done
    if port_in_use "$port"; then
        err "Could not free port $port — please kill PID(s) $pids manually and rerun"
        return 1
    fi
    ok "Port $port ($name) is now free."
}

wait_for_port() {
    local name="$1" port="$2" retries="${3:-30}"
    local i=0
    while ! nc -z 127.0.0.1 "$port" 2>/dev/null && ! nc -z ::1 "$port" 2>/dev/null; do
        i=$((i + 1))
        if [ "$i" -ge "$retries" ]; then
            err "$name did not open port $port after ${retries}s — check logs"
            return 1
        fi
        sleep 1
    done
}

# Read a single KEY from a dotenv-style file (handles values with spaces;
# avoids bash `source` which mis-parses unquoted spaces in .env files).
read_env_value() {
    local file="$1" key="$2"
    [ -f "$file" ] || return 1
    awk -F= -v k="$key" '
        /^[[:space:]]*#/ { next }
        $1 == k { sub(/^[^=]*=/, ""); sub(/[[:space:]]+#.*$/, ""); print; exit }
    ' "$file"
}

# ── If a previous run left services behind, stop them first ──────────────────
if [ -f "$PID_FILE" ]; then
    warn ".dev.pids exists — running ./stop.sh to clean up previous run…"
    bash "$ANTON_ROOT/stop.sh" || warn "stop.sh reported issues — continuing anyway"
    # stop.sh removes the PID file on success; force it gone if anything slipped through
    rm -f "$PID_FILE"
fi

# ── Ports (from .env.port — safe to source: numeric values only) ─────────────
set -a
source "$ANTON_ROOT/.env.port"
set +a

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
WAGNER_PORT="${WAGNER_BACKEND_PORT:-8001}"
DANTE_PORT="${DANTE_PORT:-9100}"

# Bach port comes from bach's own .env.local first, then .env
BACH_PORT="$(read_env_value "$BACH_ROOT/.env.local" AFBACH_VAULT_PORT 2>/dev/null \
            || read_env_value "$BACH_ROOT/.env" AFBACH_VAULT_PORT 2>/dev/null \
            || echo 8765)"
BACH_URL="$(read_env_value "$ANTON_ROOT/.env.cred.local" AFBACH_URL 2>/dev/null \
           || echo "http://[::1]:${BACH_PORT}/v1")"

# ── Cleanup ──────────────────────────────────────────────────────────────────
# Track services as we start them so we can tear down partial progress on
# Ctrl+C / SIGTERM / unexpected error.
BACH_PID=""; DANTE_PID=""; WAGNER_PID=""; BACKEND_PID=""; FRONTEND_PID=""

teardown() {
    local cause="${1:-signal}"
    # Disable further traps so SIGINT during cleanup doesn't recurse
    trap - INT TERM HUP ERR EXIT
    echo ""
    case "$cause" in
        err)    err "Startup failed — rolling back." ;;
        signal) warn "Caught signal — stopping all services…" ;;
    esac
    for pid in "$FRONTEND_PID" "$BACKEND_PID" "$WAGNER_PID" "$DANTE_PID" "$BACH_PID"; do
        [ -n "$pid" ] || continue
        # Kill the whole process group so uv/uvicorn/pnpm children go too
        local pgid
        pgid="$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
        if [ -n "$pgid" ]; then
            kill -TERM "-${pgid}" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
        else
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    # Give children a moment to flush, then force-kill stragglers
    sleep 1
    for pid in "$FRONTEND_PID" "$BACKEND_PID" "$WAGNER_PID" "$DANTE_PID" "$BACH_PID"; do
        [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null || true
    done
    bash "$ANTON_ROOT/database/db.sh" stop 2>/dev/null || true
    rm -f "$PID_FILE"
    ok "All services stopped."
    exit 0
}

trap 'teardown err' ERR
trap 'teardown signal' INT TERM HUP

# ── 0. Pre-flight: ensure every app port is free (auto-kill stale holders) ───
log "Checking ports are free…"
preflight_failed=0
free_port "Anton backend"  "$BACKEND_PORT"  || preflight_failed=1
free_port "Anton frontend" "$FRONTEND_PORT" || preflight_failed=1
[ -f "$WAGNER_ROOT/backend/alembic.ini" ] && { free_port "Wagner backend" "$WAGNER_PORT" || preflight_failed=1; }
[ -f "$DANTE_ROOT/pyproject.toml" ]      && { free_port "Dante API"      "$DANTE_PORT"  || preflight_failed=1; }
[ -f "$BACH_ROOT/pyproject.toml" ]       && { free_port "Bach vault"     "$BACH_PORT"   || preflight_failed=1; }
if [ "$preflight_failed" = 1 ]; then
    err "Aborting — could not free all ports."
    exit 1
fi
ok "All ports free."

# ── 1. Database: PostgreSQL + Redis ──────────────────────────────────────────
log "Starting PostgreSQL + Redis…"
bash "$ANTON_ROOT/database/db.sh" start
ok "Database services started."

# ── 2. Bach vault ────────────────────────────────────────────────────────────
if [ -f "$BACH_ROOT/pyproject.toml" ]; then
    log "Starting Bach vault on :${BACH_PORT}…"
    ( cd "$BACH_ROOT" && unset VIRTUAL_ENV && exec uv run bach serve ) \
        > >(prefix_lines "$MAGENTA" "bach") 2>&1 &
    BACH_PID=$!

    if wait_for_port "bach" "$BACH_PORT" 30; then
        ok "Bach vault ready at ${BACH_URL}"
    else
        warn "Bach vault not responding — backend will fall back to file-based env"
    fi
else
    warn "Bach not found at $BACH_ROOT — skipping (file env will be used)"
fi

# ── 3. Dante security API (optional) ─────────────────────────────────────────
if [ -f "$DANTE_ROOT/pyproject.toml" ]; then
    log "Starting Dante security API on :${DANTE_PORT}…"
    ( cd "$DANTE_ROOT" && unset VIRTUAL_ENV && exec uv run dante serve --port "$DANTE_PORT" ) \
        > >(prefix_lines "$PURPLE" "dante") 2>&1 &
    DANTE_PID=$!
    if wait_for_port "dante" "$DANTE_PORT" 20; then
        ok "Dante ready at http://127.0.0.1:${DANTE_PORT}"
    else
        warn "Dante did not open :${DANTE_PORT} — continuing (Anton has Dante middleware embedded)"
    fi
else
    warn "Dante not found at $DANTE_ROOT — skipping standalone server (middleware is embedded in Anton)"
fi

# ── 4. Wagner IAM backend (standalone, on :WAGNER_PORT) ──────────────────────
if [ -f "$WAGNER_ROOT/backend/alembic.ini" ]; then
    log "Running Wagner Alembic migrations…"
    (
        cd "$WAGNER_ROOT/backend"
        unset VIRTUAL_ENV
        uv run python -m alembic upgrade head 2>&1
    ) | prefix_lines "$ORANGE" "wagner-migrate" || warn "Wagner migrations failed — continuing"

    log "Starting Wagner backend on :${WAGNER_PORT}…"
    (
        cd "$WAGNER_ROOT/backend"
        unset VIRTUAL_ENV
        export BACKEND_HOST=127.0.0.1
        export BACKEND_PORT="$WAGNER_PORT"
        exec uv run python -m uvicorn app.main:app --reload --host 127.0.0.1 --port "$WAGNER_PORT"
    ) > >(prefix_lines "$ORANGE" "wagner") 2>&1 &
    WAGNER_PID=$!
    if wait_for_port "wagner" "$WAGNER_PORT" 30; then
        ok "Wagner ready at http://127.0.0.1:${WAGNER_PORT}"
    else
        warn "Wagner backend did not open :${WAGNER_PORT} — continuing (Anton has Wagner embedded)"
    fi
else
    warn "Wagner not found at $WAGNER_ROOT/backend — skipping standalone server (IAM is embedded in Anton)"
fi

# ── 5. Anton DB migrations ───────────────────────────────────────────────────
# Use `python -m alembic` instead of `uv run alembic` so the venv's possibly
# stale console-script shebangs (e.g. if .venv was created at a renamed-away
# project path) don't matter — `python -m` ignores them.
log "Running Anton Alembic migrations…"
(
    cd "$ANTON_ROOT/backend"
    unset VIRTUAL_ENV
    uv run python -m alembic upgrade head 2>&1
) | prefix_lines "$YELLOW" "migrate"
ok "Anton migrations up to date."

# ── 6. Anton backend ─────────────────────────────────────────────────────────
log "Starting Anton backend on :${BACKEND_PORT}…"
(
    cd "$ANTON_ROOT/backend"
    unset VIRTUAL_ENV
    exec uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"
) > >(prefix_lines "$BLUE" "backend") 2>&1 &
BACKEND_PID=$!

if ! wait_for_port "backend" "$BACKEND_PORT" 30; then
    err "Backend failed to start — check logs above"
    exit 1
fi
ok "Backend ready at http://localhost:${BACKEND_PORT}"

# ── 7. Anton frontend ────────────────────────────────────────────────────────
log "Starting Anton frontend on :${FRONTEND_PORT}…"
(
    cd "$ANTON_ROOT/frontend"
    exec pnpm dev
) > >(prefix_lines "$GREEN" "frontend") 2>&1 &
FRONTEND_PID=$!

# ── Persist PIDs for stop.sh ─────────────────────────────────────────────────
{
    echo "BACH_PID=${BACH_PID}"
    echo "DANTE_PID=${DANTE_PID}"
    echo "WAGNER_PID=${WAGNER_PID}"
    echo "BACKEND_PID=${BACKEND_PID}"
    echo "FRONTEND_PID=${FRONTEND_PID}"
} > "$PID_FILE"

# Don't roll back from here onward — services are launched and tracked.
# Keep the INT/TERM trap so Ctrl+C in this terminal tears the stack down cleanly.
trap - ERR

# ── Ready ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
ok "Anton stack is running  (PIDs saved to .dev.pids)"
echo -e "  ${BLUE}Anton backend${NC}    http://localhost:${BACKEND_PORT}"
echo -e "  ${GREEN}Anton frontend${NC}   http://localhost:${FRONTEND_PORT}"
echo -e "  ${YELLOW}API docs${NC}         http://localhost:${BACKEND_PORT}/docs"
[ -n "$BACH_PID" ]   && echo -e "  ${MAGENTA}Bach vault${NC}       ${BACH_URL}"
[ -n "$DANTE_PID" ]  && echo -e "  ${PURPLE}Dante API${NC}        http://127.0.0.1:${DANTE_PORT}"
[ -n "$WAGNER_PID" ] && echo -e "  ${ORANGE}Wagner backend${NC}   http://127.0.0.1:${WAGNER_PORT}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Run ./stop.sh to stop all services${NC}"
echo ""

# Stream logs until the user disconnects this shell. Closing this terminal
# does NOT stop the background services — use ./stop.sh for that.
wait
