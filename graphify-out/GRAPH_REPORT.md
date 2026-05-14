# Graph Report - alpha-forge  (2026-05-14)

## Corpus Check
- 248 files · ~417,807 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1269 nodes · 2386 edges · 40 communities detected
- Extraction: 55% EXTRACTED · 45% INFERRED · 0% AMBIGUOUS · INFERRED: 1066 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 111|Community 111]]
- [[_COMMUNITY_Community 112|Community 112]]
- [[_COMMUNITY_Community 113|Community 113]]
- [[_COMMUNITY_Community 114|Community 114]]
- [[_COMMUNITY_Community 115|Community 115]]
- [[_COMMUNITY_Community 116|Community 116]]
- [[_COMMUNITY_Community 117|Community 117]]
- [[_COMMUNITY_Community 118|Community 118]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 82 edges
2. `get()` - 77 edges
3. `LLMResponse` - 55 edges
4. `alphaforge-logger — Structured rotating-file + console logger.` - 43 edges
5. `QueryType` - 43 edges
6. `BaseLLMProvider` - 42 edges
7. `RateLimits` - 39 edges
8. `WalkForwardSplit` - 37 edges
9. `LLMGateway` - 35 edges
10. `RateLimiter` - 32 edges

## Surprising Connections (you probably didn't know these)
- `_get_page()` --calls--> `connect_existing_chrome()`  [INFERRED]
  probes/ui_probe.py → backend/app/modules/brokers/_cdp.py
- `main()` --calls--> `run()`  [INFERRED]
  llm-gateway/src/alphaforge_llm_gateway/cli.py → probes/ui_probe.py
- `main()` --calls--> `run()`  [INFERRED]
  backend/app/modules/brokers/wintwealth/wintwealth_dump.py → probes/ui_probe.py
- `main()` --calls--> `run()`  [INFERRED]
  mcp/src/alphaforge_repo_context/server.py → probes/ui_probe.py
- `cli_main()` --calls--> `run()`  [INFERRED]
  mcp/src/alphaforge_repo_context/indexer.py → probes/ui_probe.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (92): BaseLLMProvider, Interface every LLM provider adapter must implement., Return the provider's default model., Shared OpenAI-compatible completion call used by all providers., BaseLLMProvider, BenchmarkReport, BenchmarkResult, _load_rubrics() (+84 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (102): build_features_for_symbol(), build_features_for_universe(), compute_interaction_features(), Phase 2.5 — Feature Orchestrator.  Combines all feature groups (technical, relat, Build features for all stocks in the filtered universe.      Args:         max_s, Compute derived/interaction features from existing features.      These capture, Build all features for a single stock.      Args:         symbol: NSE symbol (e., compare_model_importances() (+94 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (51): ABC, BrokerSource, BrokerSource ABC + lifecycle (sync, ingest_csv, info, reset).  Schemas live in `, Adapter for one holdings provider — override `fetch()` (API) or `parse()` (CSV)., AssetClass, Holding, Broker domain enums + Pydantic schemas (Holding, SourceInfo)., SourceInfo (+43 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (70): get_current_user(), FastAPI dependencies — shared across all route modules., cmd_holdings(), cmd_rebalance(), cmd_reset(), cmd_sources(), cmd_sync(), cmd_treemap() (+62 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (73): BacktestEngine, CostModel, _load_model(), Phase 5.1 + 5.2 — Backtest Engine with Indian Market Cost Model.  Simulates trad, Compute approximate round-trip cost as a percentage.          Assumes entry_valu, Record of a single simulated trade., Walk-forward backtest engine for stock screener strategies.      Modes:     1. M, Initialize backtest engine.          Args:             top_n: Number of top pick (+65 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (31): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), Base, Base, Async database engine and session factory., EmbeddingService, get_embedding_service(), Gemini embedding service for vector memory. (+23 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (42): BaseSettings, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang() (+34 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (42): BaseModel, get_brief(), get_risk(), get_stats(), get_ticker(), get_watchlist(), Dashboard read-only feeds for the terminal home screen.  Disclaimer: Not SEBI re, BriefBlock (+34 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (42): dated_csv_path(), dump_dir(), is_csv_fresh(), live_csv_path(), Shared CSV-cache utilities for broker holdings dump modules., Raise ValueError for oversized or missing-column CSV files., read_csv(), _row_values() (+34 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (38): cdp_url(), connect_existing_chrome(), cookie_value(), find_or_open_page(), Connect to an existing Chrome started with --remote-debugging-port=PORT.  Lets y, Return (playwright, browser) attached to the running Chrome via CDP., Return the first existing page whose URL contains `match`, else open one., _verify_loopback() (+30 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (24): HoldingsAggregator, Holdings aggregator — read-only roll-up over registered BrokerSource caches.  Di, AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell, get_source_info() (+16 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (34): check_benchmarks(), compute_all_metrics(), compute_cagr(), compute_calmar_ratio(), compute_max_drawdown(), compute_portfolio_metrics(), compute_sharpe_ratio(), _compute_sortino() (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (16): AppShell(), Badge(), BootStep(), Card(), CardHeader(), Chip(), CountUp(), HudCorners() (+8 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (17): Benchmark endpoints — kicks off a background run, exposes the latest result., _run_benchmark(), _build_parser(), _format_response(), main(), _read_input(), _run(), from_env() (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (20): apply_quality_filters(), build_dataset(), build_single_stock_dataset(), compute_dataset_stats(), _get_available_symbols(), Phase 3.2 — Dataset Assembly.  Combines features (Phase 2) + labels (Phase 3.1), Apply data quality rules to the assembled dataset.      Rules:     1. Drop rows, Compute and format dataset statistics as a text report. (+12 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (14): createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, Configure and return the application root logger.      Resolution order for ever, setup_logging(), lifespan() (+6 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (11): MarketDataService, Market data service — fetches quotes, history, indices from Indian exchanges., Aggregates market data from NSE, BSE, and third-party providers., Fetch real-time quote for a symbol., # TODO: integrate with data provider (NSE API / broker feed / third-party), Fetch major Indian indices — NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT, etc., # TODO: scrape/fetch from NSE/BSE, Fetch historical OHLCV candles. (+3 more)

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (8): useHoldings(), useResetSource(), useStartLogin(), useSubmitOtp(), useSyncSource(), useUploadCsv(), PortfolioHeader(), useSourceRow()

### Community 18 - "Community 18"
Cohesion: 0.2
Nodes (13): compute_momentum_features(), compute_price_action_features(), compute_technical_features(), compute_trend_features(), compute_volatility_features(), compute_volume_features(), Phase 2.1 — Technical Indicators.  Computes ~30 technical indicators per stock u, Volatility indicators: Bollinger Bands, ATR, Keltner Channel. (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (13): apply_rules(), evaluate_baseline(), Phase 4.1 — Baseline Technical Rules Strategy.  Simple rule-based screener for c, Run baseline strategy on dataset and compute performance metrics.      Args:, RSI(14) < 35 — stock is oversold territory., Volume > 2× 20-day average (VOL_SMA_RATIO > 2.0)., MACD histogram is positive (bullish momentum)., Price is above SMA(50) — uptrend confirmation. (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.21
Nodes (11): clear_index_cache(), compute_all_relative_strength(), compute_relative_strength(), _compute_returns(), _load_index_close(), Phase 2.2 — Relative Strength Features.  Computes stock returns relative to benc, Compute relative strength vs all available benchmarks.      Args:         stock_, Clear the cached index data (e.g., between runs). (+3 more)

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (6): login(), Auth endpoints — token login only., handleSubmit(), create_access_token(), Security utilities — password hashing, JWT tokens., verify_password()

### Community 22 - "Community 22"
Cohesion: 0.24
Nodes (9): clear_fundamental_cache(), compute_52w_return(), compute_fundamental_features(), _fetch_fundamentals(), Phase 2.3 — Fundamental Features.  Fetches PE, PB, market cap, 52-week return, a, Clear the cached fundamental data., Fetch fundamental data for a single stock from yfinance.      Returns a dict wit, Compute rolling 252-day (52-week) return from Close prices. (+1 more)

### Community 23 - "Community 23"
Cohesion: 0.2
Nodes (4): useDashboardStats(), useDashboardTicker(), TerminalStats(), TerminalTicker()

### Community 24 - "Community 24"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 25 - "Community 25"
Cohesion: 0.38
Nodes (6): get_env_files(), load_env_files(), Resolve the ordered list of .env files to load.  Mirrors Next.js convention with, Return the ordered tuple of .env file paths for the given environment.      `env, Inject `.env*` files into `os.environ` in priority order (later wins).      Pyda, _repo_root()

### Community 26 - "Community 26"
Cohesion: 0.33
Nodes (5): get_logger(), Centralized logging configuration for AlphaForge backend.  Thin wrapper around t, Configure and return the application root logger., Return a child logger under the ``alphaforge`` namespace., setup_logging()

### Community 29 - "Community 29"
Cohesion: 0.5
Nodes (2): readPersisted(), writePersisted()

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (2): health_check(), Health check endpoints.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 110 - "Community 110"
Cohesion: 1.0
Nodes (1): Sync any API source whose cached data is missing or older than _STALE_SECONDS.

### Community 111 - "Community 111"
Cohesion: 1.0
Nodes (1): Fetch real-time quote for a given NSE/BSE symbol.

### Community 112 - "Community 112"
Cohesion: 1.0
Nodes (1): Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc.

### Community 113 - "Community 113"
Cohesion: 1.0
Nodes (1): Search stocks, ETFs, mutual funds by name or symbol.

### Community 114 - "Community 114"
Cohesion: 1.0
Nodes (1): Fetch OHLCV price history for charting.

### Community 115 - "Community 115"
Cohesion: 1.0
Nodes (1): # TODO: fetch live index data

### Community 116 - "Community 116"
Cohesion: 1.0
Nodes (1): # TODO: search against instrument master

### Community 117 - "Community 117"
Cohesion: 1.0
Nodes (1): # TODO: fetch historical data

### Community 118 - "Community 118"
Cohesion: 1.0
Nodes (1): Compact preview: top-level keys + first list-of-dict path with sample.

## Knowledge Gaps
- **255 isolated node(s):** `Playwright UI probe — exercises the AlphaForge frontend auth + navigation flow.`, `Return (page, browser, playwright, is_cdp) ready for use.`, `Attach to existing CDP Chrome, read Zerodha enctoken, probe Kite OMS API.  Run w`, `Read the enctoken cookie from the attached Chrome session.`, `Compact preview: top-level keys + first list-of-dict path with sample.` (+250 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 29`** (5 nodes): `ThemeProvider.tsx`, `readPersisted()`, `ThemeProvider()`, `useTheme()`, `writePersisted()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (3 nodes): `health_routes.py`, `health_check()`, `Health check endpoints.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `limiter.py`, `Shared slowapi rate limiter instance.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (2 nodes): `dashboard_seed.py`, `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 110`** (1 nodes): `Sync any API source whose cached data is missing or older than _STALE_SECONDS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 111`** (1 nodes): `Fetch real-time quote for a given NSE/BSE symbol.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 112`** (1 nodes): `Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 113`** (1 nodes): `Search stocks, ETFs, mutual funds by name or symbol.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 114`** (1 nodes): `Fetch OHLCV price history for charting.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 115`** (1 nodes): `# TODO: fetch live index data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 116`** (1 nodes): `# TODO: search against instrument master`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 117`** (1 nodes): `# TODO: fetch historical data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 118`** (1 nodes): `Compact preview: top-level keys + first list-of-dict path with sample.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 22`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 0` to `Community 2`, `Community 13`, `Community 7`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `build_features_for_symbol()` connect `Community 1` to `Community 18`, `Community 20`, `Community 14`, `Community 22`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `LLMProvider` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMProvider` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `get()` (e.g. with `_probe()` and `_fetch_fundamentals()`) actually correct?**
  _`get()` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `LLMResponse` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMResponse` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `str` (e.g. with `run()` and `_probe()`) actually correct?**
  _`str` has 44 INFERRED edges - model-reasoned connections that need verification._