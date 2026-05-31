# Probes vs Connectors

Two separate layers in AlphaForge Anton both talk to broker APIs — but for completely different reasons.

## What Is a Connector?

A **connector** is a `BrokerSource` subclass in `backend/app/modules/brokers/<broker>/`.
It is a production component: registered in `registry.py`, loaded at server startup, and called by the aggregator to serve `/portfolio/holdings`.

Examples: `ZerodhaKiteSource`, `GrowwSource`, `AngelOneSource`, `BinanceSource`.

Each connector:
- Extends `BrokerSource` (ABC in `base.py`)
- Implements `fetch() → list[Holding]` and optionally `fetch_cash() → WalletBalance`
- Runs **inside the FastAPI process** on the server's event loop
- Caches results in memory (`_cached`) and on disk (CSV dump)
- Tracks lifecycle state: `UNCONFIGURED → SYNCING → READY / ERROR`
- Is always alive — the server holds a singleton instance per broker

## What Is a Probe?

A **probe** is a standalone Python script in `probes/`.
It is a **developer tool**: run manually or via `just`, never imported by the server.

Examples: `zerodha_probe.py`, `groww_probe.py`, `ui_probe.py`, `angelone_cash_probe.py`.

Each probe:
- Is a self-contained `asyncio.run(main())` script
- Attaches to the running Chrome via CDP on `:9299` to borrow the live session
- Fires raw API calls and prints the **response shape** or **data quality summary**
- Is used during development to understand a new endpoint before writing the connector
- Is used after a connector ships to verify live data quality (`last_price ≠ 0`, `pnl_pct` consistent, etc.)
- Has no effect on production data — read-only exploration

## Side-by-Side Comparison

| | Connector (`BrokerSource`) | Probe (`probes/`) |
|---|---|---|
| **Location** | `backend/app/modules/brokers/<broker>/` | `probes/` |
| **Lifecycle** | Singleton, runs inside FastAPI, always alive | One-shot script, launched manually |
| **Who runs it** | The server aggregator on demand | Developer (or `just <broker>-probe`) |
| **Output** | `list[Holding]` consumed by `/portfolio/holdings` | Pretty-printed JSON to stdout |
| **Auth** | Reads stored session from `.cache/brokers/<slug>.bin` | Reads live cookies from Chrome CDP `:9299` |
| **Data written** | In-memory cache + CSV dump | Nothing (read-only) |
| **CI / automation** | Yes — synced by `refetch.py` on startup | Yes — `just ui-probe` is runnable in CI |
| **Purpose** | Serve production portfolio data | Explore, validate, debug |
| **Depends on server** | Is the server | No — bypasses FastAPI entirely |
| **Project imports** | Full — uses `app.modules.*`, Pydantic models | Full — can import `app.modules.*` for helpers |

## How They Relate

A probe is the **prototype** and **verification harness** for a connector:

```
1. Write a probe  →  understand the API response shape
2. Write the connector  →  implement fetch() using that shape
3. Run the probe again  →  validate live data quality after deploy
```

`zerodha_probe.py` hits `/oms/portfolio/holdings` and prints the raw shape.
`ZerodhaKiteSource.fetch()` parses that same shape into `list[Holding]`.

The probe tells you what the broker sends; the connector tells the app what that means.

## Auth Difference

| | Connector | Probe |
|---|---|---|
| **Token source** | `_http.load_session("zerodha")` — encrypted `.bin` on disk | `cookie_value()` — reads live Chrome cookie via CDP |
| **Refreshes** | On 401/403: clears session, re-attaches Chrome to re-acquire | Always reads fresh from Chrome at run time |
| **Requires Chrome** | Only for re-auth on session expiry | Always — Chrome must be open |

## Boot Probes (Third Concept)

`backend/app/modules/health/boot_probes.py` is a different thing entirely — these are **health check functions** used by `/health/boot`. They probe the system (DB, vault, LLM gateway, broker registry) at startup to populate the boot status toast. They are not development tools and are not related to `probes/`.

The naming overlap is unfortunate: `probes/` = dev exploration scripts; `boot_probes.py` = production readiness checks.

## When to Write Which

| Situation | Write a… |
|---|---|
| New broker, unknown API shape | Probe first — explore endpoints safely |
| Broker API understood, need holdings in the app | Connector |
| Connector ships but showing `last_price = 0` | Probe — compare live API vs what connector parses |
| UI feature needs validation against real holdings | `ui_probe.py` — reads JWT from localStorage, hits the live API |
| System health check on startup | Add to `boot_probes.py` |
