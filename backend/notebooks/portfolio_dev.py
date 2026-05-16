# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.14.2)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Portfolio / Brokers — Dev Playground
#
# Interactive notebook for exercising the `/portfolio/*` API surface. Two modes:
#
# 1. **In-process** (default) — `TestClient` calls the FastAPI app directly, no server needed. Fastest for iteration.
# 2. **Live HTTP** — points at a running `uvicorn` server. Use for CORS validation, real broker API calls, or frontend wiring.
#
# Toggle with `MODE` in the setup cell below.
#
# | Slug | Kind | Auth |
# |---|---|---|
# | `zerodha` | API | Browser CDP — log in to kite.zerodha.com inside the AlphaForge Chrome session. Set `ZERODHA_USER_ID` in `.env.cred.local`. |
# | `groww` | API | Browser CDP — log in to groww.in inside the AlphaForge Chrome. Set `GROWW_USER_ID`. |
# | `angelone` | API | Browser CDP — log in to angelone.in inside the AlphaForge Chrome. Set `ANGELONE_CLIENT_ID`. |
# | `indmoney` | API | Browser CDP — log in to indmoney.com inside the AlphaForge Chrome. Set `INDMONEY_USER_ID`. |
# | `tickertape` | API | Browser CDP — log in to tickertape.in inside the AlphaForge Chrome. Set `TICKERTAPE_USER_ID`. |

# %%
import json
from pathlib import Path

# MODE = "in_process"   # switch to "http" to hit a live server
MODE = "http"
BASE = "http://localhost:8000/api/v1"

if MODE == "in_process":
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    PREFIX = "/api/v1"
else:
    import httpx
    client = httpx.Client(base_url=BASE, timeout=60.0)
    PREFIX = ""


def get(path, **kw):
    r = client.get(f"{PREFIX}{path}", **kw)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def post(path, **kw):
    r = client.post(f"{PREFIX}{path}", **kw)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def pp(obj):
    """Pretty-print a JSON-serializable response body."""
    print(json.dumps(obj, indent=2, default=str))


print(f"Mode: {MODE}")

# %% [markdown]
# ## 1. List configured sources
#
# `status` is `ready` when the required env var is set in `.env.cred.local`, otherwise `unconfigured`.

# %%
_, body = get("/portfolio/sources")
for s in body["sources"]:
    print(f"  {s['slug']:14} {s['kind']:4} {s['status']:13} {s['label']}")

# %% [markdown]
# ## 2. Sync a source via API
#
# Triggers the CDP browser login + holdings fetch. The result is cached on disk — subsequent syncs skip re-login until the TTL expires.
#
# > Requires `MODE="http"` against a live server with an active browser session in Chrome.

# %%
SLUG = "zerodha"  # change to groww / angelone / indmoney / tickertape as needed
status, body = post(f"/portfolio/sources/{SLUG}/sync")
print(status)
print(json.dumps(body, indent=2, default=str)[:800])

# %% [markdown]
# ## 3. Sync all sources in parallel

# %%
status, body = post("/portfolio/sources/sync-all")
print(status)
pp(body.get("results", body))

# %% [markdown]
# ## 4. Aggregate view
#
# After sync, all source caches merge into one portfolio. Allocation groups holdings by `asset_class`.

# %%
status, body = get("/portfolio/holdings")
print("Status:", status)
print("Totals:", body["totals"])
print("\nAllocation:")
for s in body["allocation"]:
    print(f"  {s['asset_class']:12} ₹{s['value']:>14,.0f}  ({s['pct']:>5.1f}%)")
print(f"\nHoldings ({len(body['holdings'])} total):")
for h in body["holdings"]:
    print(f"  {h['symbol']:14} qty={h['quantity']:<6}  ltp=₹{h['last_price']:>10,.2f}  pnl={h['pnl_pct']:>+.1f}%")

# %% [markdown]
# ## 5. Filter by source

# %%
_, body = get("/portfolio/holdings", params={"source": "zerodha"})
print("Zerodha-only totals:", body["totals"])
for h in body["holdings"][:5]:
    print("  ", h["symbol"], h["quantity"], h["current_value"])

# %% [markdown]
# ## 6. Treemap layout
#
# Pre-computed squarified layout — frontend absolute-positions each cell using the `left_pct / top_pct / width_pct / height_pct` fields.

# %%
_, body = get("/portfolio/treemap")
for c in body["cells"][:8]:
    print(f"  {c['symbol']:14} {c['pct']:>5.1f}% @ ({c['left_pct']:>5.1f}, {c['top_pct']:>5.1f}) {c['width_pct']:>5.1f}x{c['height_pct']:>5.1f}")

# %% [markdown]
# ## 7. Rebalance suggestions
#
# Drift = actual − target. Default targets: 60% equity / 15% MF / 15% bond / 5% gold / 3% crypto / 2% cash.

# %%
_, body = get("/portfolio/rebalance")
print("Drift:")
for d in body["drift"]:
    print(f"  {d['asset_class']:12} target {d['target_pct']:>5.1f}% · actual {d['actual_pct']:>5.1f}% · drift {d['drift_pct']:>+5.1f}%")
print("\nSuggestions:")
for s in body["suggestions"]:
    print("  -", s["action"])

# %% [markdown]
# ## 8. Free cash balances  (`/portfolio/cash`)
#
# Dedicated cash surface — separate from the holdings + wallet bundle.
#
# | Endpoint | What it does |
# |---|---|
# | `GET /portfolio/cash` | Cached snapshot — instant, no browser needed |
# | `POST /portfolio/cash/sync` | Sync all cash-capable brokers concurrently |
# | `POST /portfolio/cash/{slug}/sync` | Sync a single broker |
#
# **Timing**: Zerodha uses enctoken HTTP (~1 s). Groww and Angel One open a
# fresh CDP tab (~15–25 s each). Run against a live server with Chrome open.

# %%
# Cached snapshot — always instant
status, body = get("/portfolio/cash")
print("Status:", status)
print(f"{'slug':14} {'cash':>12}  available  error")
for w in body.get("cash", []):
    avail = "✓" if w["cash_available"] else "—"
    err = w.get("cash_error") or ""
    print(f"  {w['slug']:14} ₹{w['cash']:>10,.2f}  {avail:9}  {err}")

# %%
# Sync all cash-capable brokers (Zerodha + Groww + Angel One)
# Requires MODE="http", Chrome open and logged in to each broker.
status, body = post("/portfolio/cash/sync")
print("Status:", status)
for w in body.get("cash", []):
    avail = "✓" if w["cash_available"] else "✗"
    err = f"  ERR: {w['cash_error']}" if w.get("cash_error") else ""
    print(f"  {w['slug']:14} ₹{w['cash']:>10,.2f}  {avail}{err}")

# %%
# Sync a single broker — change CASH_SLUG as needed
CASH_SLUG = "zerodha"  # zerodha | groww | angelone
status, body = post(f"/portfolio/cash/{CASH_SLUG}/sync")
print(f"Status: {status}")
if status == 200:
    w = body["cash"]
    print(f"  {w['slug']}  ₹{w['cash']:,.2f}  available={w['cash_available']}  as_of={w.get('cash_as_of')}")
else:
    pp(body)

# %% [markdown]
# ## 9. Reset in-memory state
#
# Clears the cached holdings for all sources so you can re-sync from a clean slate.

# %%
from app.modules.brokers import SOURCES

for src in SOURCES.values():
    src.reset()

status, body = get("/portfolio/sources")
for s in body["sources"]:
    print(f"  {s['slug']:14} {s['status']:13} ({s['holdings_count']} holdings)")
