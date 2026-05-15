# Graph Report - alpha-forge  (2026-05-15)

## Corpus Check
- 300 files · ~516,622 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1505 nodes · 2745 edges · 54 communities detected
- Extraction: 56% EXTRACTED · 44% INFERRED · 0% AMBIGUOUS · INFERRED: 1197 edges (avg confidence: 0.66)
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
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 149|Community 149]]
- [[_COMMUNITY_Community 150|Community 150]]
- [[_COMMUNITY_Community 151|Community 151]]
- [[_COMMUNITY_Community 152|Community 152]]
- [[_COMMUNITY_Community 153|Community 153]]
- [[_COMMUNITY_Community 154|Community 154]]
- [[_COMMUNITY_Community 155|Community 155]]
- [[_COMMUNITY_Community 156|Community 156]]
- [[_COMMUNITY_Community 157|Community 157]]
- [[_COMMUNITY_Community 158|Community 158]]
- [[_COMMUNITY_Community 159|Community 159]]
- [[_COMMUNITY_Community 160|Community 160]]
- [[_COMMUNITY_Community 161|Community 161]]
- [[_COMMUNITY_Community 162|Community 162]]
- [[_COMMUNITY_Community 163|Community 163]]
- [[_COMMUNITY_Community 164|Community 164]]
- [[_COMMUNITY_Community 165|Community 165]]
- [[_COMMUNITY_Community 166|Community 166]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 94 edges
2. `LLMProvider` - 82 edges
3. `LLMResponse` - 55 edges
4. `alphaforge-logger — Structured rotating-file + console logger.` - 46 edges
5. `QueryType` - 43 edges
6. `BaseLLMProvider` - 42 edges
7. `RateLimits` - 39 edges
8. `WalkForwardSplit` - 37 edges
9. `LLMGateway` - 35 edges
10. `BrokerSource` - 33 edges

## Surprising Connections (you probably didn't know these)
- `run()` --calls--> `main()`  [INFERRED]
  probes/ui_probe.py → mcp/src/alphaforge_repo_context/server.py
- `login()` --calls--> `post()`  [INFERRED]
  probes/ui_screens.py → backend/notebooks/portfolio_dev.py
- `run()` --calls--> `connect_existing_chrome()`  [INFERRED]
  probes/ui_probe.py → backend/app/modules/brokers/_cdp.py
- `run()` --calls--> `get()`  [INFERRED]
  probes/ui_probe.py → backend/notebooks/portfolio_dev.py
- `run()` --calls--> `main()`  [INFERRED]
  probes/ui_probe.py → llm-gateway/src/alphaforge_llm_gateway/cli.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (92): BaseLLMProvider, Interface every LLM provider adapter must implement., Return the provider's default model., Shared OpenAI-compatible completion call used by all providers., BaseLLMProvider, BenchmarkReport, BenchmarkResult, _load_rubrics() (+84 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (79): ABC, AngelOneSource, _holding_from_csv(), _holding_from_row(), Angel One holdings — BrokerSource impl over SmartAPI + CSV cache.  Free SmartAPI, Base, BrokerSource, BrokerSource ABC + lifecycle (sync, ingest_csv, info, reset).  Schemas live in ` (+71 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (102): build_features_for_symbol(), build_features_for_universe(), compute_interaction_features(), Phase 2.5 — Feature Orchestrator.  Combines all feature groups (technical, relat, Build features for all stocks in the filtered universe.      Args:         max_s, Compute derived/interaction features from existing features.      These capture, Build all features for a single stock.      Args:         symbol: NSE symbol (e., compare_model_importances() (+94 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (74): get_current_user(), FastAPI dependencies — shared across all route modules., cmd_holdings(), cmd_rebalance(), cmd_reset(), cmd_sources(), cmd_sync(), cmd_treemap() (+66 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (71): BacktestEngine, CostModel, _load_model(), Phase 5.1 + 5.2 — Backtest Engine with Indian Market Cost Model.  Simulates trad, Compute approximate round-trip cost as a percentage.          Assumes entry_valu, Record of a single simulated trade., Walk-forward backtest engine for stock screener strategies.      Modes:     1. M, Initialize backtest engine.          Args:             top_n: Number of top pick (+63 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (47): Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang(), File chunking: AST-aware for Python, regex for TS/TSX, section-based for Markdow (+39 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (36): HoldingsAggregator, Holdings aggregator — read-only roll-up over registered BrokerSource caches.  Di, AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell, get_source_info() (+28 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (42): BaseModel, get_brief(), get_risk(), get_stats(), get_ticker(), get_watchlist(), Dashboard read-only feeds for the terminal home screen.  Disclaimer: Not SEBI re, BriefBlock (+34 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (39): dump_angelone(), is_csv_fresh(), live_csv_path(), main(), Angel One holdings CSV cache — fetches via SmartAPI, caches to CSV.  TTL control, _ttl(), write_csv(), acquire_token() (+31 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (36): cdp_url(), connect_existing_chrome(), cookie_value(), find_or_open_page(), Connect to an existing Chrome started with --remote-debugging-port=PORT.  Lets y, Return (playwright, browser) attached to the running Chrome via CDP., Return the first existing page whose URL contains `match`, else open one., _verify_loopback() (+28 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (19): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), EmbeddingService, get_embedding_service(), Gemini embedding service for vector memory., float32[768] embeddings via Gemini text-embedding-004 (free tier).      Falls ba, Indexing helpers — pick → ScreenerPickEmbedding record builder., upsert_pick() (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (34): check_benchmarks(), compute_all_metrics(), compute_cagr(), compute_calmar_ratio(), compute_max_drawdown(), compute_portfolio_metrics(), compute_sharpe_ratio(), _compute_sortino() (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (6): BaseSettings, _find_repo_root(), Configuration for the repo-context MCP server.  Reads from environment (and the, Walk up from this file to find the repo root (has .git)., Settings, alphaforge-logger — Structured rotating-file + console logger.

### Community 13 - "Community 13"
Cohesion: 0.1
Nodes (29): dated_csv_path(), dump_dir(), is_csv_fresh(), live_csv_path(), Shared CSV-cache utilities for broker holdings dump modules., Raise ValueError for oversized or missing-column CSV files., read_csv(), _row_values() (+21 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (15): AppShell(), Badge(), BootStep(), Card(), CardHeader(), Chip(), CountUp(), HudCorners() (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (8): fmtINR(), fmtValue(), PortfolioView(), SourceSpotlight(), squarify(), walletAggregate(), WalletCard(), worstAspect()

### Community 16 - "Community 16"
Cohesion: 0.1
Nodes (10): useResetSource(), useStartLogin(), useSubmitOtp(), useSyncSource(), useSyncWallet(), useUploadCsv(), SourceSpotlight(), useSourceRow() (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (17): Benchmark endpoints — kicks off a background run, exposes the latest result., _run_benchmark(), _build_parser(), _format_response(), main(), _read_input(), _run(), from_env() (+9 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (20): apply_quality_filters(), build_dataset(), build_single_stock_dataset(), compute_dataset_stats(), _get_available_symbols(), Phase 3.2 — Dataset Assembly.  Combines features (Phase 2) + labels (Phase 3.1), Apply data quality rules to the assembled dataset.      Rules:     1. Drop rows, Compute and format dataset statistics as a text report. (+12 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (14): createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, Configure and return the application root logger.      Resolution order for ever, setup_logging(), lifespan() (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (11): MarketDataService, Market data service — fetches quotes, history, indices from Indian exchanges., Aggregates market data from NSE, BSE, and third-party providers., Fetch real-time quote for a symbol., # TODO: integrate with data provider (NSE API / broker feed / third-party), Fetch major Indian indices — NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT, etc., # TODO: scrape/fetch from NSE/BSE, Fetch historical OHLCV candles. (+3 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (2): AlphaForgeApp(), useTweaks()

### Community 23 - "Community 23"
Cohesion: 0.2
Nodes (13): compute_momentum_features(), compute_price_action_features(), compute_technical_features(), compute_trend_features(), compute_volatility_features(), compute_volume_features(), Phase 2.1 — Technical Indicators.  Computes ~30 technical indicators per stock u, Volatility indicators: Bollinger Bands, ATR, Keltner Channel. (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.15
Nodes (13): apply_rules(), evaluate_baseline(), Phase 4.1 — Baseline Technical Rules Strategy.  Simple rule-based screener for c, Run baseline strategy on dataset and compute performance metrics.      Args:, RSI(14) < 35 — stock is oversold territory., Volume > 2× 20-day average (VOL_SMA_RATIO > 2.0)., MACD histogram is positive (bullish momentum)., Price is above SMA(50) — uptrend confirmation. (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (12): get_symbol(), main(), module_overview(), MCP server — exposes repo-context tools over stdio.  Launch via:     python -m a, Semantic search over the AlphaForge codebase.      Returns chunks ranked by cosi, Look up a function, class, interface, or type by name.      `kind` may be one of, Summarize a module: nearest CLAUDE.md / PLAN.md / README.md + file listing., Recent git commits — optionally scoped to a path. (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (11): clear_index_cache(), compute_all_relative_strength(), compute_relative_strength(), _compute_returns(), _load_index_close(), Phase 2.2 — Relative Strength Features.  Computes stock returns relative to benc, Compute relative strength vs all available benchmarks.      Args:         stock_, Clear the cached index data (e.g., between runs). (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.2
Nodes (6): login(), Auth endpoints — token login only., handleSubmit(), create_access_token(), Security utilities — password hashing, JWT tokens., verify_password()

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (9): clear_fundamental_cache(), compute_52w_return(), compute_fundamental_features(), _fetch_fundamentals(), Phase 2.3 — Fundamental Features.  Fetches PE, PB, market cap, 52-week return, a, Clear the cached fundamental data., Fetch fundamental data for a single stock from yfinance.      Returns a dict wit, Compute rolling 252-day (52-week) return from Close prices. (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.2
Nodes (4): useDashboardStats(), useDashboardTicker(), TerminalStats(), TerminalTicker()

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 31 - "Community 31"
Cohesion: 0.38
Nodes (6): get_env_files(), load_env_files(), Resolve the ordered list of .env files to load.  Mirrors Next.js convention with, Return the ordered tuple of .env file paths for the given environment.      `env, Inject `.env*` files into `os.environ` in priority order (later wins).      Pyda, _repo_root()

### Community 32 - "Community 32"
Cohesion: 0.33
Nodes (5): get_logger(), Centralized logging configuration for AlphaForge backend.  Thin wrapper around t, Configure and return the application root logger., Return a child logger under the ``alphaforge`` namespace., setup_logging()

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (2): isActive(), TerminalTopBar()

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (2): squarify(), worst()

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 149 - "Community 149"
Cohesion: 1.0
Nodes (1): Raise RuntimeError if base_url is not on the approved list in dev mode.

### Community 150 - "Community 150"
Cohesion: 1.0
Nodes (1): Acquire enctoken from an already-running Chrome (CDP, port 9299).      If the us

### Community 151 - "Community 151"
Cohesion: 1.0
Nodes (1): Sync any API source whose cached data is missing or older than _STALE_SECONDS.

### Community 152 - "Community 152"
Cohesion: 1.0
Nodes (1): Compact preview: top-level keys + first list-of-dict path with sample.

### Community 153 - "Community 153"
Cohesion: 1.0
Nodes (1): Raise ValueError for oversized or missing-column CSV files.

### Community 154 - "Community 154"
Cohesion: 1.0
Nodes (1): Map a Groww holdings row to the shared dict shape used by dump.py.

### Community 155 - "Community 155"
Cohesion: 1.0
Nodes (1): Reload the holdings page and capture the holdings + LTP responses.      Groww's

### Community 156 - "Community 156"
Cohesion: 1.0
Nodes (1): Attach to Chrome, reload Groww's holdings page, capture the response.

### Community 157 - "Community 157"
Cohesion: 1.0
Nodes (1): Return (page, browser, playwright, is_cdp) ready for use.

### Community 158 - "Community 158"
Cohesion: 1.0
Nodes (1): Sync any API source whose cached data is missing or older than _STALE_SECONDS.

### Community 159 - "Community 159"
Cohesion: 1.0
Nodes (1): Fetch real-time quote for a given NSE/BSE symbol.

### Community 160 - "Community 160"
Cohesion: 1.0
Nodes (1): Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc.

### Community 161 - "Community 161"
Cohesion: 1.0
Nodes (1): Search stocks, ETFs, mutual funds by name or symbol.

### Community 162 - "Community 162"
Cohesion: 1.0
Nodes (1): Fetch OHLCV price history for charting.

### Community 163 - "Community 163"
Cohesion: 1.0
Nodes (1): # TODO: fetch live index data

### Community 164 - "Community 164"
Cohesion: 1.0
Nodes (1): # TODO: search against instrument master

### Community 165 - "Community 165"
Cohesion: 1.0
Nodes (1): # TODO: fetch historical data

### Community 166 - "Community 166"
Cohesion: 1.0
Nodes (1): Compact preview: top-level keys + first list-of-dict path with sample.

## Knowledge Gaps
- **281 isolated node(s):** `Capture screenshots of the terminal, portfolio, and preferences pages.  Attaches`, `Get a token from the API and stash it in localStorage so AuthGuard lets us in.`, `Playwright UI probe — exercises the AlphaForge frontend auth + navigation flow.`, `Attach to existing CDP Chrome, read Zerodha enctoken, probe Kite OMS API.  Run w`, `Read the enctoken cookie from the attached Chrome session.` (+276 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (17 nodes): `tweaks-app.jsx`, `tweaks-panel.jsx`, `AlphaForgeApp()`, `TweakButton()`, `TweakColor()`, `TweakNumber()`, `TweakRadio()`, `TweakRow()`, `TweakSection()`, `TweakSelect()`, `TweakSlider()`, `TweaksPanel()`, `TweakText()`, `TweakToggle()`, `__TwkCheck()`, `__twkIsLight()`, `useTweaks()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (3 nodes): `TerminalTopBar.tsx`, `isActive()`, `TerminalTopBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (3 nodes): `treemap.utils.ts`, `squarify()`, `worst()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (2 nodes): `limiter.py`, `Shared slowapi rate limiter instance.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (2 nodes): `dashboard_seed.py`, `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 149`** (1 nodes): `Raise RuntimeError if base_url is not on the approved list in dev mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 150`** (1 nodes): `Acquire enctoken from an already-running Chrome (CDP, port 9299).      If the us`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 151`** (1 nodes): `Sync any API source whose cached data is missing or older than _STALE_SECONDS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 152`** (1 nodes): `Compact preview: top-level keys + first list-of-dict path with sample.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 153`** (1 nodes): `Raise ValueError for oversized or missing-column CSV files.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 154`** (1 nodes): `Map a Groww holdings row to the shared dict shape used by dump.py.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 155`** (1 nodes): `Reload the holdings page and capture the holdings + LTP responses.      Groww's`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 156`** (1 nodes): `Attach to Chrome, reload Groww's holdings page, capture the response.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 157`** (1 nodes): `Return (page, browser, playwright, is_cdp) ready for use.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 158`** (1 nodes): `Sync any API source whose cached data is missing or older than _STALE_SECONDS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 159`** (1 nodes): `Fetch real-time quote for a given NSE/BSE symbol.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 160`** (1 nodes): `Fetch major Indian market indices — NIFTY 50, SENSEX, BANK NIFTY, etc.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 161`** (1 nodes): `Search stocks, ETFs, mutual funds by name or symbol.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 162`** (1 nodes): `Fetch OHLCV price history for charting.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 163`** (1 nodes): `# TODO: fetch live index data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 164`** (1 nodes): `# TODO: search against instrument master`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 165`** (1 nodes): `# TODO: fetch historical data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 166`** (1 nodes): `Compact preview: top-level keys + first list-of-dict path with sample.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 17`, `Community 28`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 0` to `Community 1`, `Community 12`, `Community 17`, `Community 7`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Text()` connect `Community 10` to `Community 1`, `Community 5`, `Community 14`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 92 inferred relationships involving `get()` (e.g. with `run()` and `_probe()`) actually correct?**
  _`get()` has 92 INFERRED edges - model-reasoned connections that need verification._
- **Are the 78 inferred relationships involving `LLMProvider` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMProvider` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `str` (e.g. with `run()` and `run()`) actually correct?**
  _`str` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `LLMResponse` (e.g. with `LLMGateway` and `LLMGateway — main entry point that ties providers, router, rate limiter, and cos`) actually correct?**
  _`LLMResponse` has 53 INFERRED edges - model-reasoned connections that need verification._