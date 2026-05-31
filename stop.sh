#!/usr/bin/env bash
# stop.sh — Stop all Anton local development services started by start.sh

set -euo pipefail

ANTON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ANTON_ROOT/.dev.pids"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo -e "${CYAN}[stop]${NC} $*"; }
ok()   { echo -e "${GREEN}[stop]${NC} $*"; }
warn() { echo -e "${YELLOW}[stop]${NC} $*"; }
err()  { echo -e "${RED}[stop]${NC} $*" >&2; }

kill_tree() {
    local name="$1" pid="$2"
    if [ -z "$pid" ]; then
        warn "${name}: no PID recorded"
        return
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
        warn "${name} (PID ${pid}) was not running"
        return
    fi
    # Kill the whole process group so uvicorn/uv/pnpm children go down too
    local pgid
    pgid="$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
    if [ -n "$pgid" ]; then
        kill -TERM "-${pgid}" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
    else
        kill -TERM "$pid" 2>/dev/null || true
    fi
    # Give it 3s, then SIGKILL the group if still alive
    for _ in 1 2 3; do
        kill -0 "$pid" 2>/dev/null || { ok "Stopped ${name} (PID ${pid})"; return; }
        sleep 1
    done
    [ -n "$pgid" ] && kill -KILL "-${pgid}" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
    ok "Force-killed ${name} (PID ${pid})"
}

kill_port() {
    local name="$1" port="$2"
    local pids
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | tr '\n' ' ' | sed 's/ $//')"
    [ -z "$pids" ] && return 0
    warn "Port $port ($name) held by PID(s) $pids — killing…"
    for pid in $pids; do kill -TERM "$pid" 2>/dev/null || true; done
    sleep 2
    for pid in $pids; do kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null || true; done
    ok "Cleared port $port ($name)."
}

# ── Load PIDs ────────────────────────────────────────────────────────────────
ANTON_ENV="$ANTON_ROOT/.env.port"
BACKEND_PORT=8000; FRONTEND_PORT=3000; WAGNER_BACKEND_PORT=8001; DANTE_PORT=9100
[ -f "$ANTON_ENV" ] && { set -a; source "$ANTON_ENV"; set +a; }

if [ ! -f "$PID_FILE" ]; then
    warn "No .dev.pids file — killing by port instead…"
    kill_port "Anton backend"  "${BACKEND_PORT:-8000}"
    kill_port "Anton frontend" "${FRONTEND_PORT:-3000}"
    kill_port "Wagner backend" "${WAGNER_BACKEND_PORT:-8001}"
    kill_port "Dante API"      "${DANTE_PORT:-9100}"
    bash "$ANTON_ROOT/database/db.sh" stop 2>/dev/null || true
    ok "All services stopped."
    exit 0
fi

BACH_PID=""; DANTE_PID=""; WAGNER_PID=""; BACKEND_PID=""; FRONTEND_PID=""
# shellcheck source=/dev/null
source "$PID_FILE"

# ── Stop background services (reverse order of start) ────────────────────────
log "Stopping Anton stack…"
kill_tree "frontend" "$FRONTEND_PID"
kill_tree "backend"  "$BACKEND_PID"
kill_tree "wagner"   "$WAGNER_PID"
kill_tree "dante"    "$DANTE_PID"
kill_tree "bach"     "$BACH_PID"

# ── Stop database ────────────────────────────────────────────────────────────
log "Stopping PostgreSQL + Redis…"
bash "$ANTON_ROOT/database/db.sh" stop 2>/dev/null && ok "Database services stopped." \
    || warn "Database services may have already been stopped."

rm -f "$PID_FILE"
echo ""
ok "All services stopped."
