# Broker CSV Dump Convention

All broker holdings dumps share a single implementation in
`backend/app/modules/brokers/dump_utils.py`. No broker-specific `*_dump.py`
file may duplicate path resolution, permission-setting, or P&L calculation.

## Output directory

| Priority | Source | Value |
|----------|--------|-------|
| 1 | `$PORTFOLIO_DUMP_DIR` env var | Absolute path, or repo-relative path resolved from repo root |
| 2 | Default | `~/.alphaforge-anton/portfolio-dumps/` |

Directory is created automatically with `chmod 700`. Each CSV file is written
with `chmod 600`.

## File naming

| File | Pattern | Purpose |
|------|---------|---------|
| Live (TTL-cached) | `{slug}-holdings-live.csv` | Re-used until TTL expires |
| Dated snapshot | `{slug}-holdings-{YYYY-MM-DD}.csv` | One per day, UTC date |

## CSV format

**Header comment (line 1)**

```
# source=<slug>  dumped_at_utc=<ISO-8601>  holdings_count=<n>
```

**Column headers (line 2) — `dump_utils.CSV_HEADERS`**

```
tradingsymbol, name, isin, exchange, quantity, average_price, last_price,
invested, current_value, pnl, pnl_pct, asset_class
```

`invested`, `current_value`, `pnl`, and `pnl_pct` are computed by
`dump_utils._row_values()` from `quantity`, `average_price`, and
`last_price`. Never recompute them in broker-specific code.

`name` and `asset_class` are optional — older dumps written before these
columns existed still validate. `asset_class` must be set when a broker source
returns mixed asset types (e.g. `zerodha_kite` writes `"equity"` only;
`zerodha_coin` writes `"etf"` or `"mutual_fund"`). When reading back a CSV row
that lacks `asset_class`, source code falls back to instrument-type lookup or
the source default. Valid values match `AssetClass` enum values: `equity`,
`mutual_fund`, `etf`, `bond`, `gold`, `crypto`, `cash`, `other`.

`name` (company / instrument display name): populate it in the broker normalizer
when the source returns it (Groww V2 → `symbolData.companyShortName`).
Zerodha's Kite holdings JSON does not include it;
`zerodha_kite_instruments.py` fetches the public Kite instruments dump
(`https://api.kite.trade/instruments`, ~3 MB, 24h TTL, cached to
`{dump_dir}/zerodha-instruments.csv`) and provides a `tradingsymbol → name`
lookup. TTL is overridable via `ZERODHA_INSTRUMENTS_TTL_SECONDS`.

## API

```python
from app.modules.brokers.dump_utils import (
    dump_dir,           # () -> Path  — resolves env var or default
    live_csv_path,      # (slug) -> Path
    dated_csv_path,     # (slug) -> Path
    is_csv_fresh,       # (slug, ttl_seconds) -> bool
    read_csv,           # (slug) -> list[dict[str, str]]
    write_csv,          # (rows, dst, *, source) -> None
    clear_csv_cache,    # (slug) -> bool — deletes live CSV, returns True if it existed
    CSV_HEADERS,        # canonical column tuple
)
```

`clear_csv_cache(slug)` is used by `POST /portfolio/refresh` to force a full
re-fetch from the broker API, bypassing the TTL. Broker sources check
`is_csv_fresh()` on every `fetch()` call — deleting the live file makes the
next sync skip the CSV path entirely.

## Reusing the I/O discipline for non-holdings data (market data)

`CSV_HEADERS` is the **holdings** contract. Market data (NSE bhavcopy OHLCV bars) is a
different shape, so `marketdata/bhavcopy_ingest.py` does **not** use `CSV_HEADERS` or widen
`dump_utils.py`. Instead it **reuses the I/O discipline** (`chmod 700` dir, the
`# source=… dumped_at_utc=…` header-comment, the `chmod 600` write) with its own column set
(`date, symbol, series, isin, open, high, low, close, volume, turnover`). The `turnover` column is
the day's traded value in ₹ — it feeds the 60-day-median liquidity universe the EB-0 panel is pinned
on; the `nse-bhavcopy` ingestion CLI normalizes both legacy cm-bhav (`TOTTRDVAL`) and 2024+ UDiFF
(`TtlTrfVal`) to ₹.

**Separate directory — `nse_data_dir()` / `$NSE_DATA_DIR`.** The raw NSE cache lives in its own dir
via the constitutional resolver `app.core.paths.resolve("NSE_DATA_DIR", "nse")` — `$NSE_DATA_DIR`
(absolute as-is, `~` expanded, relative under `$ANTON_DATA_DIR`), default `$ANTON_DATA_DIR/nse`.

### The one-time NSE ingestion helper — parallel, resumable, byte-integrity (network here; funnel offline)

`just ingest-nse FROM TO` (`marketdata/bhavcopy_cli.py`, **stdlib `urllib` + `ThreadPoolExecutor`**) is
a one-time networked TOOL, NOT the funnel. It primes NSE cookies once (browser UA, shared across
workers) and fetches each business day **in parallel** (`--workers N` / `NSE_WORKERS`, default 8;
per-request jitter + exponential backoff; a `Breaker` halves concurrency + pauses on a 429/403 burst).
It stores the **raw `.zip` (equity) + `.csv` (index) per day** under `$NSE_DATA_DIR` — never unzipped
to disk; OHLCV+turnover are read straight from the zip with stdlib `zipfile`.

- **Resumable & self-healing.** A day is "done" only if its cached file exists **and** its bytes still
  sha256-match `cache-manifest.json` **and** the zip CRC verifies (`bhavcopy_integrity`) — mere
  existence never counts. A re-run skips every verified-good day and re-fetches only missing/corrupt
  ones. **Atomic writes** (temp → `fsync` → `os.replace`) mean an interrupted download never leaves a
  half-file at the real path.
- **Integrity manifest** (`cache_manifest.py`, counts/hashes only — PII-safe, gitignored with the
  cache): per file `{sha256, byte_size, row_count, source_url, fetched_at}` + a rollup
  `{day_count, date_range, total_bytes, cache_fingerprint}`. **`--verify`** re-hashes the whole cache
  offline and exits non-zero on any missing/corrupt file — a cheap full audit, no network.
- **Determinism.** Per-day cache files + the committed panel depend only on the bytes NSE served,
  never on fetch order or `--workers`; `fetched_at` lives ONLY in the cache manifest, never the panel.
- No-network host: `--raw-dir DIR` ingests pre-downloaded archives. **$0** (HTTP I/O, not LLM — never
  metered through cage).

The loop shows a live **thread-safe progress bar** (`progress_utils.Progress`) — a `\r` block bar with
done/total days, %, the date, `cached · ⬇ fetched · ♻ refetched · ⚠ missing · ✗ failed · w workers`,
elapsed + ETA — a `Lock` guards the render. STDERR only, **only on a TTY and not `--quiet`/
`--no-progress`**, so piped / CI runs emit nothing and stay byte-identical (`just probe progress`).

`build-panel` ([panel_build.py](../backend/app/modules/marketdata/panel_build.py)) emits a
survivorship-safe **liquidity superset** (the union of the weekly point-in-time
top-250-by-median-turnover sets, `panel_universe.liquid_superset`) and writes **both** a `closes`
block (forward-filled across gaps/delistings — a held position keeps its last value) **and** a
`turnover` block (`panel_universe.align_turnover`, **0 on non-trading days, never forward-filled**).
That asymmetry is deliberate: the 0-filled turnover is what makes the funnel's per-rebalance
liquidity universe look-ahead-free (a pre-listing / delisted name has no turnover, so it can never be
picked). Gate-0 then runs at every weekly rebalance before the panel is written.

The panel is committed as a **deterministic gzip** (`factor_panel.dump_panel` → `panel.json.gz`,
`gzip.compress(…, mtime=0)`): the 500-name superset + turnover is ~20–25 MB raw but ~3–4 MB gzipped,
and `mtime=0` keeps re-runs byte-identical. `factor_panel.load_panel` gunzips `.gz` transparently and
still accepts a plain `.json` (the synthetic fixtures stay uncompressed).

**Never-buy exclusions are loaded at runtime, never committed.** The hard never-buy list is an elgar
money doc (`elgar://plan/hard-exclusion-symbols`); anton holds only the loader
(`factor_universe.load_exclusions`). Pass `--exclusions <path>` to **`build-panel`** (excluded
symbols never enter the committed superset) — use the **same** file for `eb0-real` so the runtime
price-floor agrees with build membership. Tickers never land in the repo, a fixture, or the journal.

## Adding a new broker

1. Create `backend/app/modules/brokers/{slug}/{slug}_dump.py`.
2. Import helpers from `dump_utils` — do not rewrite them.
3. Call `write_csv(rows, live_csv_path(slug), source=slug)` and
   `write_csv(rows, dated_csv_path(slug), source=slug)`.
4. Use `is_csv_fresh(slug, ttl)` to skip redundant API calls.
