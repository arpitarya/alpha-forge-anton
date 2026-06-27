"""Market-data plane — point-in-time, survivorship-safe NSE daily bars (Gate-0).

The one-time networked helper (`bhavcopy_cli`/`bhavcopy_service`/`bhavcopy_fetch`, stdlib
`urllib`+`ThreadPoolExecutor`, `just ingest-nse`) pulls legacy cm-bhav + 2024+ UDiFF archives +
the NIFTY close **as raw `.zip`/`.csv` per day** into `nse_data_dir()` (`$NSE_DATA_DIR`). It is
**parallel, resumable, and self-healing**: `cache_manifest` records per-file sha256/CRC/row counts,
a day is "done" only if its bytes still match (`bhavcopy_integrity`), atomic writes never leave a
half-file, and a `Breaker` (`throttle_utils`) halves concurrency on a 429/403 burst. `panel_build`
(`just build-panel`, offline/$0) reads the cache via `cache_read` — **re-hashing every file (the
byte-integrity Gate-0)** — and pins the top-N liquidity universe into the committed gzip
`factor_panel.Panel`. `gate0_integrity` is the no-look-ahead / no-survivorship admission test.
"""
