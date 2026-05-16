# Broker Source Integration Guide

How AlphaForge fetches, caches, and exposes holdings from a broker. Read this before adding a new source.

---

## Architecture at a glance

```
registry.py          ← process-wide {slug → BrokerSource} map
    └── BrokerSource (base.py)   ← ABC; two entry-points: fetch() + parse()
            ├── {slug}_source.py         ← the public adapter (implements BrokerSource)
            ├── {slug}_source_helper.py  ← auth + HTTP/CDP calls (pure async)
            ├── {slug}_dump.py           ← thin TTL-cache wrapper around dump_utils
            └── {slug}_csv.py            ← CSV-upload fallback parser
```

Sibling: `backend/notebooks/{slug}_dev.ipynb` — REPL-style end-to-end exercise of every `/portfolio/*` endpoint scoped to the source. Required for every new broker (see step 4 of "Register the new source" below).

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

Create these files under `backend/app/modules/brokers/{slug}/`:

| File | Purpose | Line budget | Required? |
|------|---------|------------|-----------|
| `__init__.py` | barrel export of public classes | ≤ 10 | yes |
| `{slug}_source_helper.py` | REQUIRED_ENV, auth, raw data fetch | ≤ 100 | yes |
| `{slug}_dump.py` | TTL wrappers + standalone CLI | ≤ 70 | yes |
| `{slug}_source.py` | `BrokerSource` subclass | ≤ 100 | yes |
| `{slug}_csv.py` | CSV-upload parser (may delegate to `_GrowwCSV` pattern) | ≤ 60 | yes |
| `{slug}_cash_helper.py` | CDP/HTTP capture of free-cash XHR | ≤ 100 | only if `supports_cash = True` |
| `{slug}_routes.py` | broker-specific extra endpoints | ≤ 50 | optional |

Plus these outside the module dir:

| File | Purpose | Required? |
|------|---------|-----------|
| `backend/notebooks/{slug}_dev.ipynb` | End-to-end REPL — see step 4 below | yes |
| `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` | 3-5 representative rows | yes |
| `probes/{slug}_probe.py` | XHR probe for holdings | API kinds only |
| `probes/{slug}_cash_probe.py` | XHR/HTTP probe for free cash | only if `supports_cash = True` |

Then register in `registry.py` (one line), add the env var(s) to `.env.cred.example`, and add URL/needle constants to `broker_urls.py` (cash brokers also add `{SLUG}_BALANCE_PAGE`, `{SLUG}_BALANCE_URL_NEEDLES`).

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
from app.modules.brokers.mybroker.mybroker_csv import MyBrokerCSVSource as _CSV
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
2. Set `self.refetch_seconds = int(os.getenv("{SLUG}_REFETCH_SECONDS", "3600"))` in `__init__` — TTL for the on-disk cache.
3. Override `async def fetch_cash(self) -> WalletBalance` — return a `WalletBalance(source=self.slug, cash=…, currency="INR", as_of=now, available=True)`.
4. The base class wraps it in `sync_cash()` which goes through `cash_dump.cached_sync_cash` — that consults the per-broker CSV cache (TTL-gated) before hitting the network, and persists fresh results to `<dump_dir>/broker-cash-live.csv`.

Patterns in use:

| Source | Balance page | XHR needle | Field path |
|--------|--------------|------------|-----------|
| Zerodha | n/a (direct HTTP) | `GET /oms/user/margins` (enctoken) | `data.equity.available.cash` |
| Angel One | `angelone.in/trade/funds` | `/funds/v2/getRMSLimit` (CDP) | `data.netAvailableFunds` |
| Groww | `groww.in/user/balance/inr` | `/margin/user_margin_details` (CDP) | `CASH.value` (string → float) |
| IndMoney | not supported (`supports_cash = False`; wallet card shows "Cash N/A") | | |
| Ticker Tape | not supported (`supports_cash = False`; wallet card shows "Cash N/A") | | |

Routes (mounted under `/portfolio/cash`):

- `GET /portfolio/cash` — cached snapshot of every cash-capable broker (no network); hydrates `src._cash` from `broker-cash-live.csv` on cold start.
- `POST /portfolio/cash/sync` — refresh all cash-capable brokers in parallel.
- `POST /portfolio/cash/{slug}/sync` — refresh one broker. Returns 422 if `supports_cash = False`.

Persistence: `cash_dump.py` writes one CSV file (`broker-cash-live.csv`) with one row per slug — TTL is per-row via the stored `as_of`, so each broker has its own freshness window. Never bypass this layer with a custom on-disk cache.

## Register the new source

Four steps. Do not skip step 4 — the notebook is the single artifact that proves the source works end-to-end without booting the frontend.

**1. Wire the source into the registry** — [registry.py](../backend/app/modules/brokers/registry.py):

```python
from app.modules.brokers.mybroker import MyBrokerSource

def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaKiteSource(),
        GrowwSource(),
        AngelOneSource(),
        IndMoneySource(),
        TickerTapeSource(),
        MyBrokerSource(),    # ← add here
    ]
    return {s.slug: s for s in instances}
```

**2. Declare credentials** — add the env var(s) with empty defaults to [.env.cred.example](../.env.cred.example) (tracked) so other contributors know what to fill in `.env.cred.local`.

**3. Add a CSV fixture + parser test** — drop a sample export at `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` and add a `Test{Broker}Parser` class in `backend/tests/test_brokers.py`. The shared `BrokerSource.parse()` contract is what the `/sources/{slug}/upload` endpoint relies on.

**4. Add a dev notebook (required)** — copy an existing notebook (e.g. `backend/notebooks/zerodha_dev.ipynb`) to `backend/notebooks/{slug}_dev.ipynb` and search-and-replace the slug + auth instructions. The notebook must exercise, in order:

1. `GET /portfolio/sources/{slug}` — confirm `status` transitions on env var presence
2. `POST /portfolio/sources/{slug}/sync` — trigger the live fetch
3. `POST /portfolio/sources/{slug}/upload` — confirm the CSV fallback still works
4. `GET /portfolio/holdings?source={slug}` + allocation
5. `GET /portfolio/treemap?source={slug}`
6. `GET /portfolio/rebalance?source={slug}`
7. `GET /portfolio/cash` + `POST /portfolio/cash/{slug}/sync` — only if `supports_cash = True` (otherwise assert 422)
8. Standalone `dump_{slug}()` call — bypasses FastAPI, proves the helper works alone
9. Cache reset

Both `MODE = "http"` (against a live server) and `MODE = "in_process"` (FastAPI `TestClient`) must run clean.

---

## IndMoney (`indmoney`)

US-stocks holdings from INDmoney's DriveWealth-backed brokerage account. CDP browser fetch with an on-disk cache — same pattern as Groww / Angel One. No CSV upload path.

| Detail | Value |
|--------|-------|
| Slug | `indmoney` |
| Auth | Manual login at `indmoney.com` inside the AlphaForge Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `INDMONEY_USER_ID` |
| Asset classes | `EQUITY` (US stocks — fractional shares via DriveWealth) |
| Kind | `SourceKind.API` |
| Cache TTL | `INDMONEY_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.indmoney.com/investments/us-stocks/my-us-stocks` |
| **Holdings endpoint** | `apixt-fz.indmoney.com/us-stocks-ext/api/v1/stocks/dw/user/account/holdings/?page=1&limit=N` |
| **Holdings key** | `data` — list of `{ticker, name, quantity, avg_price, live_price, invested_amount, current_value, total_profit_loss, total_percent_change, sector}` |
| **Field mapping** | `ticker→symbol`, `avg_price→avg_price`, `live_price→last_price`, `invested_amount→invested`, `current_value→current_value`, `total_profit_loss→pnl`, `total_percent_change→pnl_pct` |
| **Helpers** | [`indmoney_source_helper.py`](../backend/app/modules/brokers/indmoney/indmoney_source_helper.py), [`indmoney_dump.py`](../backend/app/modules/brokers/indmoney/indmoney_dump.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-chrome`.
2. Log in to [indmoney.com](https://indmoney.com) inside that Chrome window.
3. Set `INDMONEY_USER_ID` in `.env.cred.local`. The source auto-upgrades to `READY`.

---

## Ticker Tape (`tickertape`)

Digital gold (SafeGold) balance from Ticker Tape. Captures two XHRs on page load and combines them into a single `DIGITAL_GOLD` holding. CDP browser fetch with an on-disk cache — same pattern as Groww / Angel One. No CSV upload path.

| Detail | Value |
|--------|-------|
| Slug | `tickertape` |
| Auth | Manual login at `tickertape.in` inside the AlphaForge Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `TICKERTAPE_USER_ID` |
| Asset classes | `GOLD` (single DIGITAL_GOLD holding, quantity in grams) |
| Kind | `SourceKind.API` |
| Cache TTL | `TICKERTAPE_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.tickertape.in/portfolio/digital-gold` |
| **Profile endpoint** | `gold.api.tickertape.in/profile/v2` → `{goldBalance, averageBuyPrice, goldExponent, priceExponent}` |
| **Price endpoint** | `gold.api.tickertape.in/price?type=BUY` → `{currentPrice}` (₹/gram) |
| **Normalization** | `qty = goldBalance × 10^goldExponent`, `avg = averageBuyPrice × 10^priceExponent`, `ltp = currentPrice` |
| **Helpers** | [`tickertape_source_helper.py`](../backend/app/modules/brokers/tickertape/tickertape_source_helper.py), [`tickertape_dump.py`](../backend/app/modules/brokers/tickertape/tickertape_dump.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-chrome`.
2. Log in to [tickertape.in](https://tickertape.in) inside that Chrome window.
3. Set `TICKERTAPE_USER_ID` in `.env.cred.local`. The source auto-upgrades to `READY`.

---

## Angel One (`angelone`)

SmartAPI's free tier proved unreliable for personal sync (rate limits, TOTP friction, 401s on long-lived JWTs). AlphaForge now attaches to the running Chrome over CDP and captures the XHR Angel One's own web app makes — same pattern as Groww.

| Detail | Value |
|--------|-------|
| Slug | `angelone` |
| Auth | Manual login at `angelone.in` inside the AlphaForge Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `ANGELONE_CLIENT_ID` |
| Asset classes | `AssetClass.EQUITY` (Bonds/SGBs/MFs come back in the same response but aren't surfaced yet) |
| CSV TTL | `ANGELONE_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.angelone.in/trade/portfolio/equity` |
| **Confirmed holdings endpoint** | `POST portfolio-prod.angelone.in/family/v2/superportfolio` |
| **Holdings key** | `data.EquityPortfolio.HoldingDetail` |
| **Confirmed cash endpoint** | `POST amx-*.angelone.in/funds/v2/getRMSLimit` |
| **Cash key** | `data.netAvailableFunds` (fallback: `fundsForTrading`, `fundsAvailable`) |
| **Helpers** | [`angelone_source_helper.py`](../backend/app/modules/brokers/angelone/angelone_source_helper.py), [`angelone_cash_helper.py`](../backend/app/modules/brokers/angelone/angelone_cash_helper.py) |

**Field mapping** (probe-confirmed superportfolio row → `normalize()` → `_holding_from_row`):

| API field | `Holding` field | Notes |
|-----------|-----------------|-------|
| `tradeSymbol` | `symbol` | Upper-cased; carries the series suffix (e.g. `PGINVIT-IV`). Falls back to `symbolName`. |
| `compName` / `details` | `name` | — |
| `isin` | `isin` | — |
| `exchName` | `exchange` | Default `NSE` |
| `qty` / `total_qty` / `AvlQty` | `quantity` | — |
| `avgPrice` / `baseAvgPrice` | `avg_price` | — |
| `ltp` | `last_price` | Falls back to `avg_price` if absent |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-chrome`.
2. Log in to [angelone.in](https://angelone.in) inside that Chrome window.
3. Set `ANGELONE_CLIENT_ID` in `.env.cred.local`. The source auto-upgrades to `READY`.

AlphaForge never sees your password or TOTP — login + 2FA happen in your own Chrome; the backend just reads the authenticated XHR off the wire.

**Mutual funds**: not exposed by the equity holdings page. For MF, use the CSV upload fallback (`/sources/angelone/upload`) with an Angel One MF export.

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
| Angel One | [angelone_dev.ipynb](../backend/notebooks/angelone_dev.ipynb) | CDP browser fetch (`angelone.in`) |
| IndMoney | [`indmoney_dev.ipynb`](../backend/notebooks/indmoney_dev.ipynb) | CDP browser fetch (`indmoney.com/investments/us-stocks/my-us-stocks`) |
| Ticker Tape | [`tickertape_dev.ipynb`](../backend/notebooks/tickertape_dev.ipynb) | CDP browser fetch (`tickertape.in/portfolio/digital-gold`) |

Every new broker must ship a notebook in this list — see step 4 of [Register the new source](#register-the-new-source).

## XHR probes

Probe scripts in `backend/scripts/` attach to Chrome and print every
matching XHR shape. Run these **before** implementing `normalize()` to
discover the real endpoint URL and response key names.

| Broker | Probe script | Technique |
|--------|-------------|-----------|
| Zerodha | [zerodha_probe.py](../probes/zerodha_probe.py) | Reads `enctoken` cookie → direct Kite OMS REST calls |
| Groww | [groww_probe.py](../probes/groww_probe.py) | XHR interception on page reload |
| Angel One | [angelone_probe.py](../probes/angelone_probe.py) | XHR interception across holdings + funds pages |
| IndMoney | [indmoney_probe.py](../probes/indmoney_probe.py) | XHR interception on dashboard reload |
| Ticker Tape | [tickertape_probe.py](../probes/tickertape_probe.py) | XHR interception on portfolio reload |

```bash
uv run python probes/zerodha_probe.py
uv run python probes/groww_probe.py
uv run python probes/angelone_probe.py
uv run python probes/indmoney_probe.py
uv run python probes/tickertape_probe.py
```

Zerodha's probe is different: rather than intercepting XHRs, it reads the
`enctoken` cookie from Chrome and fires direct REST calls against the Kite
OMS API (`/oms/portfolio/holdings`, `/oms/portfolio/positions`,
`/oms/user/profile`, `/oms/user/margins`). Useful for verifying the token
is still valid and inspecting the live holdings shape.

Sections in each notebook:
1. Source info — verify `status: ready`
2. Sync — triggers CDP fetch + CSV cache (API sources) / Upload CSV (CSV sources)
3. Holdings — filtered by slug
4. Allocation breakdown
5. Treemap
6. Rebalance / drift
7. Standalone dump (API sources only — bypasses FastAPI)
8. Reset in-memory cache

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
