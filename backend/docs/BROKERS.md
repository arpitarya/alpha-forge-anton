# Broker Sources — Setup & Usage

> Where to download each broker's CSV, where credentials go, and how to exercise the API end-to-end.

The portfolio module aggregates holdings from five sources. Each source is one of two kinds:

- **CSV** — user uploads an export. The broker offers no free API; this is the only legal path.
- **API** — pulled programmatically. AlphaForge attaches over CDP to an authenticated Chrome session.

| Source | Slug | Kind | Where to get the data |
|---|---|---|---|
| Zerodha (equity + ETF + COIN MF) | `zerodha` | API | CDP session — log in to [kite.zerodha.com](https://kite.zerodha.com) in the AlphaForge Chrome (see below) |
| Groww | `groww` | API | CDP web-app fetch — log in to [groww.in](https://groww.in) in the AlphaForge Chrome |
| Angel One | `angelone` | API | CDP web-app fetch — log in to [angelone.in](https://angelone.in) in the AlphaForge Chrome (see below) |
| INDmoney (Indian equity, MF, US stocks, gold) | `indmoney` | API | CDP web-app fetch — log in to [indmoney.com](https://indmoney.com) in the AlphaForge Chrome |
| Ticker Tape (SGBs, Gold ETFs, gold funds) | `tickertape` | API | CDP web-app fetch — log in to [tickertape.in](https://tickertape.in) in the AlphaForge Chrome |

> This module reads holdings only — no orders are placed.

---

## Why so many CSVs?

| Broker | Free public API? | Notes |
|---|---|---|
| Zerodha (Kite Connect) | **No** — ₹2000/mo per app | We fetch equity/ETF from `/oms/portfolio/holdings` and COIN MF from `/api/mf/holdings` via the enctoken captured over CDP. |
| Groww | **No** | We attach to the authenticated web app over CDP and capture the holdings XHR. |
| Angel One | **No** stable free API for personal use | We attach to the authenticated web app over CDP and capture the `/family/v2/superportfolio` XHR. |
| INDmoney | **No** public API | CDP web-app fetch (XHR endpoint pending probe). |
| Ticker Tape | **No** public API | CDP web-app fetch (XHR endpoint pending probe). |

We chose the honest path: free + official + reproducible. As paid integrations get added (Kite Connect later, etc.), they slot into the same `BrokerSource` ABC without rewriting routes or the frontend.

---

## Angel One — CDP setup

SmartAPI's free tier proved unreliable for personal sync (rate limits, TOTP friction, frequent 401s), so AlphaForge attaches to the running Chrome over CDP and captures the XHR the Angel One web app itself makes — same pattern as Groww.

1. Start Chrome with the debugging port (one-time):

   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
       --remote-debugging-port=9299 \
       --user-data-dir="$HOME/.cache/alphaforge-chrome"
   ```

2. Log in to [angelone.in](https://angelone.in) inside that Chrome window.
3. Add your client ID to `.env.cred.local`:

   ```bash
   ANGELONE_CLIENT_ID=<your_angel_one_client_id>
   ```

4. Trigger a sync:

   ```bash
   curl -X POST http://localhost:8000/api/v1/portfolio/sources/angelone/sync
   ```

If the session has expired the first attempt fails fast and the next call re-opens the login page (you finish 2FA in your own browser — AlphaForge never sees your password or OTP).

---

## Endpoints

All paths are prefixed with `/api/v1`.

### Read

| Method | Path | Description |
|---|---|---|
| `GET` | `/portfolio/holdings?source=<slug>` | Aggregated holdings + totals + allocation. Omit `source` for all. |
| `GET` | `/portfolio/treemap?source=<slug>` | Pre-computed treemap layout (left/top/width/height in %). |
| `GET` | `/portfolio/rebalance` | Drift vs target allocation + suggestions. |
| `GET` | `/portfolio/sources` | List all sources + status + last sync time. |
| `GET` | `/portfolio/sources/{slug}` | Single source info. |
| `GET` | `/portfolio/cash` | Cached free-cash snapshot for all cash-capable brokers (instant). |

### Write

| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/portfolio/sources/{slug}/upload` | multipart `file` | CSV ingest. Errors with 400 on API sources. |
| `POST` | `/portfolio/sources/{slug}/sync`   | — | Pull from upstream. Errors with 400 on CSV sources. |
| `POST` | `/portfolio/sources/{slug}/reset`  | — | Clear cached holdings (lets you re-upload). |
| `POST` | `/portfolio/cash/sync` | — | Sync free-cash for all cash-capable brokers concurrently (Zerodha ~1 s, Groww/Angel One ~15–25 s each via CDP). |
| `POST` | `/portfolio/cash/{slug}/sync` | — | Sync free-cash for one broker. Returns 422 if the slug does not support cash. |

### Unified `Holding` shape

```json
{
  "source": "zerodha",
  "asset_class": "equity",
  "symbol": "RELIANCE",
  "name": null,
  "isin": "INE002A01018",
  "quantity": 120,
  "avg_price": 2410.0,
  "last_price": 2914.05,
  "invested": 289200.0,
  "current_value": 349686.0,
  "pnl": 60486.0,
  "pnl_pct": 20.91,
  "exchange": "NSE",
  "as_of": "2026-04-26T17:31:00+00:00"
}
```

---

## Auto-refetch

On startup, the server launches a background task (`brokers/refetch.py`) that polls every 60 seconds and calls `sync()` on any source whose data is older than its TTL. TTL is controlled per-broker in `.env`:

```ini
ZERODHA_REFETCH_SECONDS=3600
GROWW_REFETCH_SECONDS=3600
ANGELONE_REFETCH_SECONDS=3600
INDMONEY_REFETCH_SECONDS=3600
TICKERTAPE_REFETCH_SECONDS=3600
```

**Key behaviour:**
- The first sync is always manual (`POST /portfolio/sources/{slug}/sync`). Auto-refetch only kicks in after a source has been synced at least once.
- Sources with status `UNCONFIGURED` or actively `SYNCING` are skipped.
- Set `*_REFETCH_SECONDS=0` to disable auto-refetch for a specific broker.
- `GET /portfolio/sources` returns `refetch_seconds` per source so the frontend can display when the next auto-sync is due.

---

## Dev workflows

### 1. Pytest suite (in-process, no server needed)

```bash
cd backend
pdm run pytest tests/test_brokers.py -v
```

Tests cover:
- Each CSV parser against a fixture export (column-shape resilience).
- `HoldingsAggregator` totals / allocation / treemap geometry / rebalance.
- All HTTP routes (`/sources`, `/upload`, `/sync`, `/holdings`, `/treemap`, `/rebalance`, `/reset`) via `TestClient`.

Add new fixtures to `backend/tests/fixtures/broker_csvs/` — the parser tests are organized one class per source so it's clear where to drop a new shape.

### 2. CLI smoke tester

```bash
# List sources
pdm run python scripts/dev_brokers.py sources

# Upload one CSV
pdm run python scripts/dev_brokers.py upload zerodha tests/fixtures/broker_csvs/zerodha_holdings.csv

# Upload all fixtures in one go (handy first-run check)
pdm run python scripts/dev_brokers.py upload-all

# Read aggregates
pdm run python scripts/dev_brokers.py holdings
pdm run python scripts/dev_brokers.py treemap --source zerodha
pdm run python scripts/dev_brokers.py rebalance

# Trigger Angel One pull (requires CDP Chrome session — see above)
pdm run python scripts/dev_brokers.py sync angelone

# Reset
pdm run python scripts/dev_brokers.py reset zerodha
```

Override the API base via `AF_API`:

```bash
AF_API=http://localhost:8765/api/v1 pdm run python scripts/dev_brokers.py sources
```

### 3. Jupyter playground

```bash
cd backend && pdm run jupyter lab notebooks/portfolio_dev.ipynb
```

Toggle `MODE = "in_process"` ↔ `"http"` to switch between `TestClient` and a live server. Useful for parser debugging (in-process) vs CORS / frontend integration testing (http).

### 4. Frontend

The `/portfolio` page consumes the same endpoints via `useHoldings`, `useTreemap`, `useRebalance`, `useSources` hooks (see `frontend/src/lib/queries.ts`). Upload happens via `useUploadCsv`; the `<SourcesPanel/>` component renders a per-source row with an upload-or-sync button.

---

## Adding a new source

See [docs/broker-source-integration.md](../../docs/broker-source-integration.md) for the full file-layout contract. Short version:

1. Create the broker package under `backend/app/modules/brokers/<slug>/` — `{slug}_source.py`, `{slug}_source_helper.py`, `{slug}_dump.py`, `{slug}_csv.py`, and `__init__.py`. The source extends `BrokerSource`; set `slug`, `label`, `kind`, and override **either** `parse(stream, filename)` (CSV) **or** `async fetch()` (API).
2. Register it in `backend/app/modules/brokers/registry.py` (one line in `_build_sources()`).
3. Add a fixture CSV at `backend/tests/fixtures/broker_csvs/<slug>_holdings.csv` and a `Test<YourSource>Parser` class in `tests/test_brokers.py`.
4. **Add a dev notebook** at `backend/notebooks/<slug>_dev.ipynb` — copy an existing notebook (e.g. `zerodha_dev.ipynb`) and replace the slug. Required: this is how the source is verified end-to-end without booting the frontend.
5. Add an entry to the matrix at the top of this file.

That's it — the routes, aggregator, treemap layout, frontend `<SourcesPanel/>`, and CLI tester all pick it up automatically.
