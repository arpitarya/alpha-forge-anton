# Broker Source Integration Guide

How AlphaForge fetches, caches, and exposes holdings from a broker. Read this before adding a new source.

---

## Architecture at a glance

```
registry.py          ← process-wide {slug → BrokerSource} map
    └── BrokerSource (base.py)   ← ABC; two entry-points: fetch() + parse()
            ├── {slug}_source.py      ← the public adapter (implements BrokerSource)
            ├── {slug}_source_helper.py  ← auth + HTTP/CDP calls (pure async)
            ├── {slug}_dump.py        ← thin TTL-cache wrapper around dump_utils
            └── csv.py                ← CSV-upload fallback parser
```

`dump_utils.py` is shared across every broker — path resolution, file permissions, CSV headers, and P&L computation all live there.

---

## Two source kinds

| Kind | `SourceKind` | Entry-point | When to use |
|------|-------------|-------------|-------------|
| API | `SourceKind.API` | `fetch()` | Broker has an endpoint you can call (with auth) |
| CSV | `SourceKind.CSV` | `parse()` | Broker only exports a downloadable CSV |

API sources also implement `parse()` as a manual CSV fallback — the `/sources/{slug}/upload` endpoint calls it.

---

## Data flow — API source (Zerodha / Groww pattern)

```
GET /api/v1/brokers/{slug}/sync
        │
        ▼
BrokerSource.sync()          (base.py — sets status SYNCING → READY / ERROR)
        │
        ▼
{slug}_source.fetch()        (checks CSV TTL first, then calls helper)
        │
        ├─ CSV cache hit → read_csv() → list[Holding]
        │
        └─ cache miss
                │
                ▼
        {slug}_source_helper  (auth: CDP enctoken / browser fetch)
                │
                ▼
        broker API / JS eval  (raw list[dict])
                │
                ▼
        write_csv() via dump_utils  (writes live + dated files)
                │
                ▼
        _holding_from_row()   → list[Holding]
```

---

## File checklist for a new broker

Create these six files under `backend/app/modules/brokers/{slug}/`:

| File | Purpose | Line budget |
|------|---------|------------|
| `__init__.py` | barrel export of public classes | ≤ 10 |
| `{slug}_source_helper.py` | REQUIRED_ENV, auth, raw data fetch | ≤ 100 |
| `{slug}_dump.py` | TTL wrappers + standalone CLI | ≤ 70 |
| `{slug}_source.py` | `BrokerSource` subclass | ≤ 100 |
| `csv.py` | CSV-upload parser (may delegate to `_GrowwCSV` pattern) | ≤ 60 |
| `{slug}_routes.py` | (optional) broker-specific extra endpoints | ≤ 50 |

Then register in `registry.py` (one line).

---

## `{slug}_source_helper.py` — what it must export

```python
REQUIRED_ENV: tuple[str, ...] = ("MYBROKER_USER_ID",)

def env(key: str) -> str:
    return os.getenv(key, "").strip()

# Acquire auth credential (enctoken, access_token, session cookie, …)
async def acquire_token(force: bool = False) -> str: ...

# Call broker API; returns raw list[dict] with at least:
#   tradingsymbol, isin, exchange, quantity, average_price, last_price
async def fetch_holdings_json(token: str) -> list[dict[str, Any]]: ...
```

`REQUIRED_ENV` drives the `SourceStatus.READY` check in `__init__` — if any env var is missing the source stays `UNCONFIGURED` and the UI surfaces that clearly.

---

## `{slug}_dump.py` — thin TTL wrapper (copy this template)

```python
"""MyBroker holdings CSV cache.

TTL controlled by MYBROKER_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.mybroker.mybroker_dump
    python -m app.modules.brokers.mybroker.mybroker_dump --force-login
"""
from __future__ import annotations

import asyncio, os, sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.mybroker.mybroker_source_helper import acquire_token, fetch_holdings_json

logger = get_logger("brokers.mybroker_dump")
SLUG = "mybroker"

def _ttl() -> int:
    return int(os.getenv("MYBROKER_REFETCH_SECONDS", "3600"))

def live_csv_path() -> Path:         return _du.live_csv_path(SLUG)
def is_csv_fresh() -> bool:          return _du.is_csv_fresh(SLUG, _ttl())
def read_csv() -> list[dict]:        return _du.read_csv(SLUG)
def write_csv(rows, dst: Path):      _du.write_csv(rows, dst, source=SLUG)


async def dump_mybroker(*, force_login: bool = False) -> Path:
    token = await acquire_token(force=force_login)
    rows = await fetch_holdings_json(token)
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _du.dated_csv_path(SLUG))
    logger.info("MyBroker: dumped %d holdings → %s", len(rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_mybroker(force_login=force))
    except Exception as e:
        logger.error("MyBroker dump failed: %s", e)
        return 1
    print(path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## `{slug}_source.py` — the BrokerSource subclass (copy this template)

```python
from __future__ import annotations
from typing import IO

import httpx
from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.mybroker.csv import MyBrokerCSVSource as _CSV
from app.modules.brokers.mybroker.mybroker_dump import is_csv_fresh, live_csv_path, read_csv, write_csv
from app.modules.brokers.mybroker.mybroker_source_helper import REQUIRED_ENV, acquire_token, env, fetch_holdings_json

logger = get_logger("brokers.mybroker")
__all__ = ["MyBrokerSource", "REQUIRED_ENV", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty   = float(r.get("quantity")      or 0)
    avg   = float(r.get("average_price") or 0)
    ltp   = float(r.get("last_price")    or 0)
    inv   = qty * avg
    cur   = qty * ltp
    pnl   = cur - inv
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        isin=r.get("isin") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl,
        pnl_pct=(pnl / inv * 100) if inv else 0.0,
        exchange=r.get("exchange") or "NSE",
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(g("tradingsymbol") or "").upper(), isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0), exchange=g("exchange") or None,
    )


class MyBrokerSource(BrokerSource):
    slug  = "mybroker"
    label = "My Broker"
    kind  = SourceKind.API
    notes = (
        "Manual login: log in to mybroker.com inside the AlphaForge Chrome "
        "(started with --remote-debugging-port=9299). "
        "Set MYBROKER_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        holdings = _CSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("MyBroker: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            token = await acquire_token()
            rows  = await fetch_holdings_json(token)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning("MyBroker: auth rejected (%s) — forcing re-login", status)
                clear_session("mybroker")
                token = await acquire_token(force=True)
                rows  = await fetch_holdings_json(token)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("MyBroker: fetched %d holdings → cached to CSV", len(out))
        return out
```

---

## Wallet cash (free balance in the broker)

A source can optionally expose its free-cash figure to power the Portfolio
wallet strip. To opt in:

1. Set the class attribute `supports_cash = True`.
2. Override `async def fetch_cash(self) -> WalletBalance` — return a
   `WalletBalance(source=self.slug, cash=…, currency="INR", as_of=now)`.
3. The base class wraps it in `sync_cash()` which catches exceptions and
   stores an "unavailable" balance so a Kite/SmartAPI hiccup never breaks
   the wallets endpoint.

Patterns in use:

| Source | Endpoint / mechanism |
|--------|----------------------|
| Zerodha | `GET /oms/user/margins` — reuses the Kite enctoken; reads `data.equity.available.cash`. Force-relogin on 401/403 |
| Angel One | `GET /rest/secure/angelbroking/user/v1/getRMS` — `data.availablecash` (falls back to `net` / `availablelimitmargin`). Force-relogin on 401/403 |
| Groww | `groww/groww_cash_helper.py` — opens a fresh tab at `groww.in/v2/balance` over CDP, registers a response listener on the dashboard's own XHR (`/api/user/v*/balance`, `/userbalance/v1`, etc.), DFS-scans the JSON for any `availableMargin` / `availableBalance` / `walletBalance` field, then closes the tab |
| Wint Wealth | not yet supported (`supports_cash = False`; wallet card shows "Cash N/A") |

Routes:

- `GET /portfolio/wallets` — list of `WalletInfo` (slug, label, cash, currency, holdings_value, holdings_count, pnl, pnl_pct, last_synced_at)
- `POST /portfolio/wallets/sync` — refresh cash on every source that opts in (parallel)
- `POST /portfolio/wallets/{slug}/sync` — refresh one broker (used by the "⟳ Refresh" button in the source spotlight)

## Register the new source

In [registry.py](../backend/app/modules/brokers/registry.py):

```python
from app.modules.brokers.mybroker import MyBrokerSource

def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaKiteSource(),
        GrowwSource(),
        WintWealthSource(),  # ← already wired
        MyBrokerSource(),    # ← add here
    ]
    return {s.slug: s for s in instances}
```

---

## Wint Wealth (`wintwealth`)

Fixed-income platform (corporate bonds, NCDs, SGBs). No public API — uses the CDP browser-fetch pattern identical to Groww.

| Detail | Value |
|--------|-------|
| Slug | `wintwealth` |
| Auth | CDP browser fetch (`fetch_holdings_via_browser`) |
| `REQUIRED_ENV` | `WINTWEALTH_USER_ID` |
| Asset classes | `AssetClass.BOND` (default), `AssetClass.GOLD` (SGBs) |
| CSV TTL | `WINTWEALTH_REFETCH_SECONDS` (default `3600`) |
| **Confirmed endpoint** | `api.wintwealth.com/investments/v2?investmentType=CURRENT&productType=BOND` |
| **Trigger page** | `wintwealth.com/portfolio/bonds/` |
| **Holdings key** | `investments` (list inside the JSON response) |

**Field mapping** (probe-confirmed):

| API field | `normalize()` key | Notes |
|-----------|------------------|-------|
| `isin` | `isin` | ISIN code |
| `productName` | `name` | Issuer name |
| `scripCode` | `tradingsymbol` | e.g. `1090NFL28` |
| `totalQuantity` | `quantity` | Number of bonds held |
| `investment` | → `average_price` | Total invested ÷ qty |
| `currentValue` | → `last_price` | Total current value ÷ qty |
| `productType` | `asset_type` | `BOND` → `bond`, `SGB`/`GOLD` → `gold` |

**Setup**: log in to `wintwealth.com` inside the AlphaForge Chrome session (port 9299), then set `WINTWEALTH_USER_ID` in `.env.cred.local`. The source auto-upgrades to `READY`.

**Asset-type mapping**: `productType` from each row drives the class — `SGB` or `GOLD` → `AssetClass.GOLD`; everything else → `AssetClass.BOND`. CSV-cached rows default to `AssetClass.BOND`.

**Standalone dump**:

```bash
python -m app.modules.brokers.wintwealth.wintwealth_dump
python -m app.modules.brokers.wintwealth.wintwealth_dump --force-login
ls ~/.alphaforge/portfolio-dumps/wintwealth-*
```

**Dev notebook**: [backend/notebooks/wintwealth_dev.ipynb](../backend/notebooks/wintwealth_dev.ipynb)

**XHR probe** (run before implementing `normalize()` to discover the real API shape):

```bash
cd backend && uv run python scripts/wintwealth_probe.py
```

[backend/scripts/wintwealth_probe.py](../backend/scripts/wintwealth_probe.py) attaches to the AlphaForge Chrome, reloads the portfolio page, and prints a compact shape summary of every matching XHR. Look for a response containing `isin`, `units`, `currentPrice`, or `securityName` — those fields confirm you've found the holdings endpoint. Use the URL to update `_NEEDLES` and the key names to refine `normalize()` in `wintwealth_source_helper.py`.

---

## Angel One (`angelone`)

Full-service broker with a **free official API** (SmartAPI). Auth is fully
headless — no Chrome / CDP attach required.

| Detail | Value |
|--------|-------|
| Slug | `angelone` |
| Auth | SmartAPI: `loginByPassword` (client code + MPIN + local TOTP) → `jwtToken` |
| `REQUIRED_ENV` | `ANGELONE_API_KEY`, `ANGELONE_CLIENT_ID`, `ANGELONE_MPIN`, `ANGELONE_TOTP_SECRET` |
| Asset classes | `AssetClass.EQUITY` (SmartAPI's `getAllHolding` returns equity only) |
| CSV TTL | `ANGELONE_REFETCH_SECONDS` (default `3600`) |
| **Login endpoint** | `apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByPassword` |
| **Holdings endpoint** | `apiconnect.angelone.in/rest/secure/angelbroking/portfolio/v1/getAllHolding` |
| **Holdings key** | `data.holdings` |

**Field mapping** (SmartAPI response → `_holding_from_row`):

| API field | `Holding` field | Notes |
|-----------|-----------------|-------|
| `tradingsymbol` | `symbol` | Upper-cased |
| `isin` | `isin` | — |
| `exchange` | `exchange` | `NSE` / `BSE` |
| `quantity` | `quantity` | — |
| `averageprice` | `avg_price` | Note: no underscore (SmartAPI quirk) |
| `ltp` | `last_price` | Falls back to `close` if absent |

**Setup**:

1. Register a free app at [smartapi.angelbroking.com](https://smartapi.angelbroking.com/) — pick "Trading" app type — to get an API key.
2. Enable TOTP on your Angel One account (Profile → Settings → 2FA). Copy the base32 secret shown under the QR code.
3. Fill `ANGELONE_API_KEY`, `ANGELONE_CLIENT_ID`, `ANGELONE_MPIN`, `ANGELONE_TOTP_SECRET` in `.env.cred.local`. The source auto-upgrades to `READY`.

AlphaForge derives the 6-digit TOTP locally via `pyotp` — the shared secret never leaves the machine. The acquired `jwtToken` is encrypted on disk via `_http.save_session` (same Fernet key as other brokers).

**Mutual funds**: SmartAPI's free tier exposes equity holdings only. For MF, use the CSV upload fallback (`/sources/angelone/upload`) with an Angel One MF export.

**Standalone dump**:

```bash
python -m app.modules.brokers.angelone.angelone_dump
python -m app.modules.brokers.angelone.angelone_dump --force-login
ls ~/.alphaforge/portfolio-dumps/angelone-*
```

---

## Dev notebooks

One notebook per broker lives in `backend/notebooks/`. Each exercises all
`/portfolio/*` endpoints scoped to that broker and works in both
`MODE="http"` (live server) and `MODE="in_process"` (FastAPI test client).

| Broker | Notebook | Auth |
|--------|----------|------|
| Zerodha | [zerodha_dev.ipynb](../backend/notebooks/zerodha_dev.ipynb) | CDP enctoken (`kite.zerodha.com`) |
| Groww | [groww_dev.ipynb](../backend/notebooks/groww_dev.ipynb) | CDP browser fetch (`groww.in`) |
| Wint Wealth | [wintwealth_dev.ipynb](../backend/notebooks/wintwealth_dev.ipynb) | CDP browser fetch (`wintwealth.com`) |

## XHR probes

Probe scripts in `backend/scripts/` attach to Chrome and print every
matching XHR shape. Run these **before** implementing `normalize()` to
discover the real endpoint URL and response key names.

| Broker | Probe script | Technique |
|--------|-------------|-----------|
| Zerodha | [zerodha_probe.py](../backend/scripts/zerodha_probe.py) | Reads `enctoken` cookie → direct Kite OMS REST calls |
| Groww | [groww_probe.py](../backend/scripts/groww_probe.py) | XHR interception on page reload |
| Wint Wealth | [wintwealth_probe.py](../backend/scripts/wintwealth_probe.py) | XHR interception on page reload |

```bash
cd backend && uv run python scripts/zerodha_probe.py
cd backend && uv run python scripts/groww_probe.py
cd backend && uv run python scripts/wintwealth_probe.py
```

Zerodha's probe is different: rather than intercepting XHRs, it reads the
`enctoken` cookie from Chrome and fires direct REST calls against the Kite
OMS API (`/oms/portfolio/holdings`, `/oms/portfolio/positions`,
`/oms/user/profile`, `/oms/user/margins`). Useful for verifying the token
is still valid and inspecting the live holdings shape.

Sections in each notebook:
1. Source info — verify `status: ready`
2. Sync — triggers CDP fetch + CSV cache
3. Upload CSV — offline fallback
4. Holdings — filtered by slug
5. Allocation breakdown
6. Treemap
7. Rebalance / drift
8. Standalone dump (Wint Wealth only — bypasses FastAPI)
9. Reset in-memory cache

---

## Auth patterns in use

### CDP enctoken (Zerodha)

Chrome is started externally with `--remote-debugging-port=9299`. The helper attaches over CDP via `_cdp.py`, reads the `enctoken` cookie after the user logs in manually, then caches it via `_http.save_session()`. Subsequent calls skip CDP entirely until the token is rejected (401/403).

Key helpers: `connect_existing_chrome`, `find_or_open_page`, `cookie_value` from `app.modules.brokers._cdp`.

### CDP browser fetch (Groww)

Similar CDP attach, but instead of reading a cookie the helper executes a `fetch()` call inside the authenticated page context and returns the JSON response directly. Used when the broker's API is not publicly documented or requires browser-side cookies that can't be trivially extracted.

Key helper: `fetch_holdings_via_browser` from `groww_source_helper.py`.

### Session caching

Both patterns use `_http.load_session` / `save_session` to persist the acquired credential across process restarts. The session file lives under `~/.alphaforge/sessions/{slug}.json` with `chmod 600`.

---

## CSV cache rules

All CSV I/O goes through `dump_utils` — never reimplement in broker code:

```python
from app.modules.brokers.dump_utils import (
    live_csv_path,    # (slug) -> Path  — {slug}-holdings-live.csv
    dated_csv_path,   # (slug) -> Path  — {slug}-holdings-YYYY-MM-DD.csv
    is_csv_fresh,     # (slug, ttl_seconds) -> bool
    read_csv,         # (slug) -> list[dict[str, str]]
    write_csv,        # (rows, dst, *, source) -> None
)
```

CSV output directory: `$PORTFOLIO_DUMP_DIR` env var or `~/.alphaforge/portfolio-dumps/` (see [broker-csv-dumps.md](broker-csv-dumps.md)).

---

## `Holding` fields

All fields the portfolio layer cares about:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source` | `str` | yes | broker slug |
| `asset_class` | `AssetClass` | yes | usually `EQUITY` |
| `symbol` | `str` | yes | trading symbol, upper-cased |
| `isin` | `str \| None` | no | — |
| `quantity` | `float` | yes | — |
| `avg_price` | `float` | yes | — |
| `last_price` | `float` | yes | — |
| `invested` | `float` | yes | `qty × avg_price` |
| `current_value` | `float` | yes | `qty × last_price` |
| `pnl` | `float` | yes | `current_value − invested` |
| `pnl_pct` | `float` | yes | `pnl / invested × 100` |
| `exchange` | `str \| None` | no | `"NSE"` default |

---

## Environment variables

Add to `.env.example` and `.env.cred.example`:

```bash
# MyBroker
MYBROKER_USER_ID=           # required — triggers READY status
MYBROKER_REFETCH_SECONDS=3600  # optional TTL, default 1h
```

The `REQUIRED_ENV` tuple in `{slug}_source_helper.py` must list every variable that must be non-empty before the source is usable.

---

## Quick sanity check after wiring up

```bash
# Run standalone dump (bypasses FastAPI, tests auth + CSV write end-to-end)
python -m app.modules.brokers.mybroker.mybroker_dump

# Force a fresh login
python -m app.modules.brokers.mybroker.mybroker_dump --force-login

# Check the output
ls ~/.alphaforge/portfolio-dumps/mybroker-*
```
