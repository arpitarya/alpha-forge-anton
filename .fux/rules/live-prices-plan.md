---
id: live-prices-plan
domain: general
type: narrative
status: active
created: 2026-06-04
updated: 2026-06-04
---
# Live prices — design plan

**Status:** _Plan only — no implementation yet._
**Owner:** picks an approach below, then writes the focused PR.

## What's live today

| Surface | Source | Refresh |
|---|---|---|
| Compact bar / Portfolio totals | `HoldingsAggregator.totals()` over broker `cached` lists | Per `_STALE_SECONDS` (3600s) when `/portfolio/holdings` is hit |
| Today's P&L | Sum of `current_value × day_change_pct/100` per holding | Same — only as fresh as the last broker sync |
| Wallet `last_price` / `pnl` | Broker source `fetch()` (Kite, Groww, AngelOne, IndMoney, TickerTape) | Sync-triggered, ~hourly |
| Terminal ticker / watchlist | `dashboard_ticker_items` / `dashboard_watchlist_items` DB rows; `price`/`change`/`tone` are the **last snapshot written** | Never updates automatically today |
| USD/INR rate | `fx.get_inr_per_usd()` → open.er-api.com | 1h CSV cache |

`day_change_pct` is wired into `Holding` and read from Zerodha Kite (`day_change_percentage`). Other brokers fall through to `0.0` until we either parse it from their existing payloads or fetch quotes ourselves — addressed below.

## Goal

A continuous stream of last-traded prices feeding three surfaces:

1. **Compact bar** — net worth + today's P&L tick as the market ticks (5–15s perceived freshness).
2. **Terminal ticker strip** — indices/commodities/large caps roll with live prices.
3. **Watchlist card** — per-symbol price + day-change line refresh in place.

Constraints we hold:
- Single-user app — no fan-out/multiplexing pressure.
- Self-hosted — no managed pub/sub. SQLite/Postgres + a Python process.
- Market data licensing — only sources we already have a session for (Kite via CDP, IndMoney US via CDP) or free quote APIs.
- Off-hours behaviour — must degrade gracefully when markets are closed.

## Option A — 15s server polling + frontend refetch

Cheapest to ship. Add a `QuoteService` that, every 15s during market hours, fetches LTP for all "subscribed" symbols (= union of holdings + ticker + watchlist) via Kite quote API (NSE/BSE) and a USD quote source (e.g. yfinance/AlphaVantage) for US tickers. Writes back to a `live_quotes` table keyed by `(symbol, exchange)`. Aggregator + dashboard read from this table when present.

- **Pros:** stays inside the FastAPI process, no new infra, easy to reason about, works off-hours (skip the loop), bounded quote-API calls per minute.
- **Cons:** 15s latency floor, batch quote APIs have request-size caps (~500 symbols/call), still polls the broker — wastes their rate limit, no per-tick UX.
- **Schema:** one new table `live_quotes(symbol, exchange, last_price, day_change_pct, as_of)` + an index on `(symbol, exchange)`.
- **Frontend:** existing TanStack `refetchInterval` drops from 30s → 5s on `/dashboard/stats|ticker|watchlist`.

## Option B — Server polling + SSE push to frontend

Same backend loop as Option A, but instead of frontend polling, expose `GET /dashboard/stream` as a Server-Sent Events endpoint. On each backend tick, broadcast a delta `{symbol, last_price, day_change_pct}` to all subscribed clients.

- **Pros:** smooth UX (sub-second visual updates after backend tick); no wasted HTTP overhead on the frontend.
- **Cons:** adds an in-process broadcaster; need to handle reconnects + auth on the long-lived stream; sse is one-way (fine here).
- **Effort:** ~1 extra day on top of Option A.

## Option C — Kite Ticker WebSocket for NSE + Option A for the rest

For NSE/BSE symbols, use Zerodha's `KiteTicker` WebSocket — it streams tick-by-tick once subscribed. For US symbols (NVDA, etc.) and indices we can't reach via Kite (some commodities), fall back to the 15s polling loop. Funnel both into the same `live_quotes` table; broadcast over SSE to the frontend.

- **Pros:** true real-time on the bulk of holdings (Indian equities); single canonical store; minimum API hits.
- **Cons:** requires a valid Kite session at all times (Kite tokens rotate daily — we'd need a re-auth flow); WebSocket lifecycle adds operational complexity; ticker reconnect logic must be solid; only works for instruments Kite exposes.
- **Effort:** ~3–5 days.

## Recommended path

Stage it:

1. **Phase 1 (Option A, 2 days):** Build `QuoteService` + `live_quotes` table + Kite quote-API polling on a 15s loop during market hours. Wire `aggregator.totals()` to prefer `live_quotes.last_price` over `Holding.last_price` when present. Drop frontend `refetchInterval` to 5s. Acceptance: net worth and today's P&L move during market hours without manual sync; off-hours show last close.
2. **Phase 2 (Option B add-on, 1 day):** Convert the frontend from polling to SSE. Keep the polling endpoints as a fallback for clients that can't hold a stream open.
3. **Phase 3 (Option C, only if Phase 2 latency feels slow):** Add Kite Ticker for NSE symbols. Keep the polling loop alive as the fallback path.

## Open questions to resolve before Phase 1

- Where do US/crypto quotes come from? IndMoney's API isn't documented for quote streaming — likely need yfinance/AlphaVantage/Coingecko. Pick one source per asset class.
- How do we model "market hours"? Hard-code NSE 09:15–15:30 IST initially; revisit when we have non-NSE symbols.
- Where does Kite's token live? It's currently in the IndMoney/Zerodha CDP-session pattern — quote API needs the same access token. Reuse `acquire_enctoken` or move to a longer-lived API key.
- Symbol-key normalisation: ticker item "NIFTY 50" vs Kite `NSE:NIFTY 50` vs holding `RELIANCE`. Need a `(symbol, exchange)` resolver before subscribing.

## Files this will touch (Phase 1 sketch)

- `backend/app/modules/quotes/quote_service.py` (new) — the 15s loop.
- `backend/app/modules/quotes/quote_repo.py` (new) — `live_quotes` upsert/read.
- `backend/alembic/versions/*_live_quotes.py` (new) — schema.
- `backend/app/modules/brokers/aggregator.py` — prefer live_quotes when fresh.
- `backend/app/modules/dashboard/dashboard_repo.py` — refresh ticker / watchlist `price`/`change` rows from live_quotes on each list call.
- `frontend/src/modules/dashboard/dashboard.query.ts` — drop `refetchInterval` from 30s → 5s.
