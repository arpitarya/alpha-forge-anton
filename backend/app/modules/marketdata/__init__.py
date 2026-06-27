"""Market-data plane — point-in-time, survivorship-safe NSE daily bars (Gate-0).

The free NSE bhavcopy is ingested into a cache that reuses the broker `dump_utils` I/O
discipline (`dump_dir`, chmod 700/600, `# source=…` header-comment) but with its own OHLCV
columns. `gate0_integrity` is the no-look-ahead / no-survivorship admission test every
universe must pass before any backtest reads it.
"""
