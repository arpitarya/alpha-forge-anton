# Broker CSV Dump Convention

All broker holdings dumps share a single implementation in
`backend/app/modules/brokers/dump_utils.py`. No broker-specific `*_dump.py`
file may duplicate path resolution, permission-setting, or P&L calculation.

## Output directory

| Priority | Source | Value |
|----------|--------|-------|
| 1 | `$PORTFOLIO_DUMP_DIR` env var | Absolute path, or repo-relative path resolved from repo root |
| 2 | Default | `~/.alphaforge/portfolio-dumps/` |

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
invested, current_value, pnl, pnl_pct
```

`invested`, `current_value`, `pnl`, and `pnl_pct` are computed by
`dump_utils._row_values()` from `quantity`, `average_price`, and
`last_price`. Never recompute them in broker-specific code.

`name` (company / instrument display name) is optional — older dumps written
before the column existed still validate. Populate it in the broker normalizer
when the source returns it (Groww V2 → `symbolData.companyShortName`,
Wint Wealth → `productName`). Zerodha's Kite holdings JSON does not include it;
`zerodha_instruments.py` fetches the public Kite instruments dump
(`https://api.kite.trade/instruments`, ~3 MB, 24h TTL, cached to
`{dump_dir}/zerodha-instruments.csv`) and provides a `tradingsymbol → name`
lookup that is applied in `_holding_from_row` / `_holding_from_csv`. TTL is
overridable via `ZERODHA_INSTRUMENTS_TTL_SECONDS`.

## API

```python
from app.modules.brokers.dump_utils import (
    dump_dir,          # () -> Path  — resolves env var or default
    live_csv_path,     # (slug) -> Path
    dated_csv_path,    # (slug) -> Path
    is_csv_fresh,      # (slug, ttl_seconds) -> bool
    read_csv,          # (slug) -> list[dict[str, str]]
    write_csv,         # (rows, dst, *, source) -> None
    CSV_HEADERS,       # canonical column tuple
)
```

## Adding a new broker

1. Create `backend/app/modules/brokers/{slug}/{slug}_dump.py`.
2. Import helpers from `dump_utils` — do not rewrite them.
3. Call `write_csv(rows, live_csv_path(slug), source=slug)` and
   `write_csv(rows, dated_csv_path(slug), source=slug)`.
4. Use `is_csv_fresh(slug, ttl)` to skip redundant API calls.
