# Graph Report - anton  (2026-06-16)

## Corpus Check
- 474 files · ~2,088,736 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2937 nodes · 5384 edges · 91 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 2281 edges (avg confidence: 0.7)
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
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 119|Community 119]]
- [[_COMMUNITY_Community 178|Community 178]]
- [[_COMMUNITY_Community 201|Community 201]]
- [[_COMMUNITY_Community 202|Community 202]]
- [[_COMMUNITY_Community 203|Community 203]]
- [[_COMMUNITY_Community 204|Community 204]]
- [[_COMMUNITY_Community 205|Community 205]]
- [[_COMMUNITY_Community 206|Community 206]]
- [[_COMMUNITY_Community 207|Community 207]]
- [[_COMMUNITY_Community 208|Community 208]]
- [[_COMMUNITY_Community 209|Community 209]]
- [[_COMMUNITY_Community 210|Community 210]]
- [[_COMMUNITY_Community 211|Community 211]]
- [[_COMMUNITY_Community 212|Community 212]]
- [[_COMMUNITY_Community 213|Community 213]]
- [[_COMMUNITY_Community 214|Community 214]]
- [[_COMMUNITY_Community 215|Community 215]]
- [[_COMMUNITY_Community 216|Community 216]]
- [[_COMMUNITY_Community 217|Community 217]]
- [[_COMMUNITY_Community 218|Community 218]]
- [[_COMMUNITY_Community 219|Community 219]]
- [[_COMMUNITY_Community 220|Community 220]]
- [[_COMMUNITY_Community 221|Community 221]]
- [[_COMMUNITY_Community 222|Community 222]]
- [[_COMMUNITY_Community 223|Community 223]]
- [[_COMMUNITY_Community 224|Community 224]]
- [[_COMMUNITY_Community 225|Community 225]]
- [[_COMMUNITY_Community 226|Community 226]]
- [[_COMMUNITY_Community 227|Community 227]]
- [[_COMMUNITY_Community 228|Community 228]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 174 edges
2. `QueryType` - 80 edges
3. `Message` - 69 edges
4. `HoldingsAggregator` - 57 edges
5. `ProviderResponse` - 55 edges
6. `alphaforge-logger — Structured rotating-file + console logger.` - 46 edges
7. `SessionMeta` - 37 edges
8. `connect_existing_chrome()` - 36 edges
9. `evaluate()` - 36 edges
10. `ToolSchema` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Tool ABC + ToolRegistry` --semantically_similar_to--> `domain_role.py filename grammar`  [INFERRED] [semantically similar]
  concierge/docs/compare/19-tool-calling.md → convention/python.md
- `_quote()` --calls--> `get()`  [INFERRED]
  probes/signals_review_probe.py → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `_holding()` --calls--> `Holding`  [INFERRED]
  probes/signals_review_probe.py → /Users/arpitarya/my_programs/alpha-forge/backend/app/modules/portfolio/portfolio_models.py
- `_series_fn()` --calls--> `get()`  [INFERRED]
  probes/signals_backtest_probe.py → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `Phase 3 prompt-caching probe — standalone, no API, no CDP.  Asserts: cacheable-p` --uses--> `Message`  [INFERRED]
  probes/claude_cache_probe.py → concierge/llm/src/alphaforge_anton_llm/types.py

## Hyperedges (group relationships)
- **Concierge 8-Block Prompt Assembly** — 4_prompt_builder, 4_holdings_snapshot, 4_user_intent_document, 4_long_term_memory, 4_news_aggregator [EXTRACTED 0.90]
- **Agentic Plan-Execute-Verify Chain** — 17_agentic_loop, 25_verifier_pass, plan_agent_loop, 21_search_web_tool [INFERRED 0.80]
- **Broker Holdings Aggregation Pipeline** — implement_brokersource_abc, implement_broker_registry, implement_holdings_aggregator, brokers_cdp_session, brokers_unified_holding_shape [EXTRACTED 0.85]
- **Fux subsumes graphify + memory + narrative docs** — concept_fux_engine, concept_graphify_graph, concept_doc_per_change [EXTRACTED 1.00]
- **Authoring-pattern guides (guide/comparison/verdict-first)** — concept_guide_pattern, doc_comparison_guide, concept_verdict_first [INFERRED 0.80]
- **Broker source → dump_utils CSV → portfolio aggregation** — module_brokers, concept_dump_utils, module_portfolio [EXTRACTED 1.00]
- **Writing a new probe (script + credentials + CDP + register + recipe)** —  [EXTRACTED 1.00]
- **Probe runtime prerequisites** —  [EXTRACTED 1.00]
- **Credential resolution chain (env to vault)** —  [EXTRACTED 1.00]
- **Governance Ledger Copy Flow** — fux_graph_05_final_governance_ledger, fux_graph_05_final_copy_button, fux_graph_05_final_governed_subgraph_copied, fux_graph_05_final_rule_summary [INFERRED 0.85]
- **Communities Lens Across Views** — labels_none_view, laptop_default_view, f3_fux_community_view, existing_tab_view [INFERRED 0.80]
- **Fux graph viewer chrome (legend + hover tooltip + edge-language + minimap)** — node_type_legend, labels_hover_node_tooltip, labels_hover_edge_language, labels_hover_minimap [INFERRED 0.80]
- **Governance ledger flow (panel + governed rules + copy subgraph + orange edges)** — fux_graph_03_settled_governance_ledger, fux_graph_03_settled_governed_rules, fux_graph_03_settled_copy_subgraph_action, fux_graph_03_settled_orange_edges [EXTRACTED 1.00]
- **Community/macro graph layouts across views** — f4_fux_community_view, final_macro_view, f3_graphify_view, rtab_collapsed_view [INFERRED 0.75]
- **Fux graph macro views (god node selection states)** — fux_graph_04_macro_view, fux_graph_02_settled_view, fux_graph_04_macro_get_node, fux_graph_02_settled_health_node [INFERRED 0.85]
- **Fux graph v2 redesign states** — v2_macro_view, v2_ledger_collapsed_view, solar_hero_view [INFERRED 0.75]
- **Governance ledger feature across views** — solar_hero_governance_ledger, solar_hero_copy_subgraph_button, v2_macro_view [INFERRED 0.70]
- **Macro view + governance ledger + edge legend + node types** —  [EXTRACTED 1.00]
- **Governance ledger listing governed rules with copy action** —  [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (200): detect_action(), Action confirmation — detect a mutating intent in the user's message and emit a, A structured pending-action card for a mutating intent, else None., _extract_equity_holdings(), Drill into the superportfolio response to pull out HoldingDetail rows., next(), month_spend_usd(), Cage metering adapter — record every completion's spend into the Cage ledger.  C (+192 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (172): AngelOneSource, _capture_holdings_via_reload(), _ensure_logged_in(), fetch_holdings_via_browser(), normalize(), Angel One — CDP login + holdings fetch via the authenticated browser context.  S, Map a superportfolio HoldingDetail row to the shared dict shape., _to_float() (+164 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (186): _amain(), `just backtest` entry — replay the active config over real cached history (§10.5, render(), _close(), BTSeries, _cache_file(), _download(), load_series() (+178 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (167): capture_angelone_cash(), _pick_cash(), Angel One — capture free-cash balance via CDP from the funds page.  Probe-confir, _to_float(), main(), Print Angel One free cash via CDP capture of /funds/v2/getRMSLimit.  Attaches to, _capture(), main() (+159 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (100): ABC, default_model(), health(), NewsSource, ProviderAdapter, ProviderHealth, NewsSource abstract base class — the contract every source must implement., The provider's default model id — the first entry in `providers.json`. (+92 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (107): _doc_id(), _hits(), is_investment(), main(), _mtime(), check(), _fixture(), main() (+99 more)

### Community 6 - "Community 6"
Cohesion: 0.02
Nodes (108): Angel One source, Binance source (crypto), Groww source, IndMoney source (US stocks), Ticker Tape source (digital gold), Zerodha Kite source, Zerodha Coin source (ETF/MF), Absolute imports + package public surface (+100 more)

### Community 7 - "Community 7"
Cohesion: 0.03
Nodes (46): NewsAggregator, NewsAggregator — fans out to all enabled sources in parallel, deduplicates., BraveSource, Brave Search source — free 2k req/month, web search fallback., BseAnnouncementsSource, BSE corporate announcements — uses BSE's public JSON API (no auth required)., deduplicate(), Deduplication — URL-canonical + title-hash; keeps the most recent copy. (+38 more)

### Community 8 - "Community 8"
Cohesion: 0.03
Nodes (73): HoldingsAggregator, _inr_invested(), _inr_value(), AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell (+65 more)

### Community 9 - "Community 9"
Cohesion: 0.03
Nodes (87): Cloud vision (Gemini Flash) for images/PDFs, Nightly cross-session summary, Dependency injection + fakes, Explicit fact extraction table, Followup model inheritance, Intent-to-model routing, Per-module Jupyter notebooks, Offline-state UX (queue + auto-retry) (+79 more)

### Community 10 - "Community 10"
Cohesion: 0.03
Nodes (82): Live Per-Query Fan-out over Polling Rationale, News Ingestion Decision, News Source Expansion Backlog, One-File NewsSource Extensibility Contract, StockTwits Source (proposed), Full Session-Cached Snapshot Rationale, Holdings Context Injection, Agentic Loop (Plan-Execute) (+74 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (58): BaseSettings, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang() (+50 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (60): cached_sync_cash(), load_cached_cash(), _path(), Shared on-disk CSV cache for broker free-cash balances.  One file, one row per b, Check CSV cache first; only call fetch_cash() if the cache is stale., Return cached WalletBalance if the row exists and is within TTL, else None., Return persisted WalletBalance regardless of TTL — for display only., Upsert one broker's cash row; leaves other brokers' rows untouched. (+52 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (57): build_report(), _friction_net(), _max_drawdown(), Closed round-trips → a `BacktestReport`. Pure: no I/O, no clock (§10.5).  Two co, gross P&L minus the explicit, per-trade frictions (no tax)., Deepest peak-to-trough on a cumulative-P&L curve → (₹, % of peak profit)., BacktestReport, Shapes for the Phase 5 backtest — replay the active config over history (§10.5). (+49 more)

### Community 14 - "Community 14"
Cohesion: 0.04
Nodes (37): streamBootSync(), diagnose(), groupByReason(), reloadAction(), slugList(), truncate(), announce(), BootGate() (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.05
Nodes (48): Base, DashboardTickerItem, DashboardWatchlistItem, SQLAlchemy ORM models for the terminal dashboard feeds.  Single-user app: ticker, One symbol that scrolls in the global terminal ticker bar., One row in the terminal-side Watchlist panel., add_ticker(), add_watchlist() (+40 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (50): dump_angelone(), is_csv_fresh(), live_csv_path(), main(), Angel One holdings CSV cache — fetches via CDP browser, caches to CSV.  TTL cont, _ttl(), write_csv(), _adapter_and_pricing() (+42 more)

### Community 17 - "Community 17"
Cohesion: 0.04
Nodes (26): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), IAM tables — users, refresh tokens, API keys, audit log.  Revision ID: a3c9f2e1b, upgrade(), AppShell(), downgrade(), Remove IAM tables — IAM is now owned by Wagner.  Revision ID: b3d6f8a2c9e1 Revis, Badge() (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.07
Nodes (37): _bin(), _dir(), get(), list_docs(), Bridge to the elgar plan store — subprocess, same pattern as `fux_bridge`.  Savi, Write a doc into the store; returns its `elgar://plan/<id>` ref., All store docs (`{id, status, title}`), optionally filtered by id prefix., Docs in a collection (`{id, status, title}`), optionally filtered by id prefix. (+29 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (31): createApiKey(), encryptCredentials(), extendSession(), getLoginKey(), getMe(), _importPublicKey(), listApiKeys(), listSessions() (+23 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (30): _broker_detail(), probe_backend(), probe_brokers(), probe_database(), probe_llm(), probe_vault(), System readiness probes used by /health/boot. Each probe returns a BootService s, BootReport (+22 more)

### Community 21 - "Community 21"
Cohesion: 0.06
Nodes (37): boot_probes.py (health checks), Broker registry.py, CDP Chrome session on port 9299, Connector (BrokerSource subclass), Frontend data flow (component -> query -> transformer -> service), Gemini text-embedding-004 (768d), Backend layered architecture (routes -> service -> repo), @alphaforge/logger Node package (pino) (+29 more)

### Community 22 - "Community 22"
Cohesion: 0.07
Nodes (37): afbach Vault, AngelOne Broker, probes/<broker>_probe.py, Broker XHR Probe, Chrome DevTools Protocol (CDP), app.modules.brokers._cdp Module, CDP Port 9299, connect_existing_chrome Helper (+29 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (13): usePlan(), usePlanDrift(), useProjection(), useSavePlan(), useHoldings(), useResetSource(), useStartLogin(), useSubmitOtp() (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.12
Nodes (23): Communities Legend (Community 0..30+ colored swatches), Node Info Panel (Click a node to inspect), Graphify Graph — Multi-Community Force Layout (F3), Distributed Blue Community Clusters, Fux Graph — Community Layout F4 (162 communities), Circular Ring Arrangement of Community Nodes around Central Hub, Fux Graph — Macro Ring Layout (162 communities, orange theme), Copy Governed Subgraph Button (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (16): complete(), CompleteIn, eval_run(), EvalIn, get_symbol(), main(), module_overview(), MCP server — exposes repo-context tools over stdio.  Launch via:     python -m a (+8 more)

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (18): _capture_holdings_via_reload(), _ensure_logged_in(), _extract_holdings_list(), fetch_holdings_via_browser(), _looks_like_holding(), _merge_ltps(), normalize(), _pick() (+10 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (20): Highlighted node: health (~26 edges), Overview minimap, Fux Graph — Initial load (Communities lens, 163 communities), God node: get (function, 766 edges), Fux Graph — Node inspect (get function, 766 edges), Edge language legend (governs/references/calls/contains/related), Governance ledger panel (6 of 7048 edges), Lens panel (Knowledge/Communities, Heat/Path) (+12 more)

### Community 28 - "Community 28"
Cohesion: 0.13
Nodes (8): downloadThread(), threadToMarkdown(), imagesFromClipboard(), handleKeyDown(), handlePaste(), handleSubmit(), runCommand(), resolveCommand()

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (18): Focused Function Node (broker module, 37 edges), Node Detail Tooltip (backend/app/modules/broker), Orange Edge Fan from Focused Node, Fux Graph — Communities Mode, Node Neighbourhood Focus, Dense Community Cluster (blue), Labeled Frontend Nodes (Chatbot.tsx, dashboard.routes.tsx), Overview Minimap, Fux Graph — Zoomed Community with Visible Labels (+10 more)

### Community 30 - "Community 30"
Cohesion: 0.12
Nodes (17): Angel One Broker, CDP Chrome Session Capture, Groww Broker, INDmoney Broker, Ticker Tape Broker, Zerodha Broker, Alpha Chat, AlphaForge Anton (+9 more)

### Community 31 - "Community 31"
Cohesion: 0.14
Nodes (14): SolarOrb component, Alpha Forge Hi-Fi.html design spec, ravel-ui / solar-ui design system, ThemeProvider + useTheme (data-theme/data-accent), solar-orb-ball Implementation Log, solar-orb-ball Plan, solar-orb-ball playground index.html, solar-orb-ball README (+6 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (2): useDashboardStats(), TerminalStats()

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (11): NewsAggregator, Deduplicator (URL-canonical + title-hash), NewsItem schema, NewsSource ABC, NewsSourceSettings ORM (Fernet-encrypted keys), RedditSource (asyncpraw), RssSource adapter (rss_feeds.yaml), News Module Plan (+3 more)

### Community 34 - "Community 34"
Cohesion: 0.24
Nodes (11): Governance Ledger Panel (5 of 7048 edges), inr-normalization Governed Node, Labeled Backend Nodes (db.py, demo.py, dated_routes.py), Fux Graph — After Checks with Governance Ledger, Visible Subgraph Copied Toast, Copy Governed Subgraph Button, Governance Ledger Panel, Highlighted Governed Edges (orange) (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (11): Frontend file nodes (SessionGroup.tsx, ChatPanel.tsx, NodeProject.tsx, notifications.store.ts), Overview minimap, Fux Graph Default Dense Cluster View, Copy governance subgraph button, Governance ledger panel (jsr-normalization, day-pnl, holdings-sum-equals-total, portfolio-valuation), Fux Graph Hero with Governance Ledger, Scattered community clusters with governance edges, Fux Graph v2 with Ledger Collapsed (+3 more)

### Community 36 - "Community 36"
Cohesion: 0.22
Nodes (7): createLogger(), getLogger(), get_logger(), Centralized logging configuration for AlphaForge Anton backend.  Thin wrapper ar, Configure and return the application root logger., Return a child logger under the ``alphaforge_anton`` namespace., setup_logging()

### Community 37 - "Community 37"
Cohesion: 0.24
Nodes (10): Anton app icon (@3x) — rounded dark squircle, orange ascending bars + rising arrow, Anton app icon: rounded dark tile containing the ascending bar-and-arrow symbol, Anton app icon (PNG): rounded dark tile with ascending bar-and-arrow symbol, Anton lockup (@2x) — symbol + ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton lockup (@3x) — high-res symbol + gray ALPHA FORGE, light ANTON, orange TRADING TERMINAL, Anton Lockup — symbol + 'ALPHA FORGE / ANTON / TRADING TERMINAL' wordmark, Anton lockup (PNG): symbol plus ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton Symbol — orange gradient ascending bar chart with rising arrow (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (6): classifyIntent(), providerDefault(), resolveProviderAuto(), resolveTopAuto(), activeModelFor(), lookup()

### Community 39 - "Community 39"
Cohesion: 0.28
Nodes (4): aggregateAll(), aggregateSelected(), currencySymbol(), fmtMoneyShort()

### Community 40 - "Community 40"
Cohesion: 0.28
Nodes (4): available(), Per-provider token-bucket rate limiter., Refills `rate` tokens per second up to `capacity`., TokenBucket

### Community 41 - "Community 41"
Cohesion: 0.32
Nodes (4): extractDetail(), kindFromStatus(), toApiError(), shouldRetry()

### Community 42 - "Community 42"
Cohesion: 0.39
Nodes (5): assetClassCounts(), bucketOf(), equitySubOf(), isInvitReit(), isUSEquity()

### Community 43 - "Community 43"
Cohesion: 0.32
Nodes (8): health function node (convergeImpl, 26 edges), Fux Graph Macro Settled (health node, Communities lens), Edge language legend (governs, references, calls, contains, related), get function god node (766 edges), Fux Knowledge Graph Engine UI, Lens panel (Knowledge / Communities / Heat / Path), Node Types legend (function, code-file, class, narrative, memory, regulatory, formula, invariant, rule), Fux Graph Macro View (get god node)

### Community 44 - "Community 44"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 46 - "Community 46"
Cohesion: 0.4
Nodes (2): requestPath(), skipRefreshRetry()

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (2): Notification(), severityIcon()

### Community 48 - "Community 48"
Cohesion: 0.5
Nodes (2): handleFooterSubmit(), handleKeyDown()

### Community 49 - "Community 49"
Cohesion: 0.4
Nodes (1): Alembic env.py — async migration runner.

### Community 50 - "Community 50"
Cohesion: 0.5
Nodes (3): dashboard ticker + watchlist items  Revision ID: 1d8f1014a7d4 Revises: 640eee61b, _table(), upgrade()

### Community 55 - "Community 55"
Cohesion: 0.83
Nodes (3): aspectRatio(), squarify(), worstAspect()

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (2): reduceEvent(), sanitizeContent()

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (2): isActive(), TerminalTopBar()

### Community 65 - "Community 65"
Cohesion: 0.67
Nodes (3): LLM Research Agent Plan, LLM Research Workspace Plan, Master Plan Index

### Community 66 - "Community 66"
Cohesion: 0.67
Nodes (3): Stylized 'A' monogram mark (orange gradient), AlphaForge brand logo (orange/grey 'A' monogram + ALPHA FORGE wordmark), ALPHA FORGE wordmark text

### Community 67 - "Community 67"
Cohesion: 0.67
Nodes (3): Backend Server :8000, Frontend Server :3000, just dev Command

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 102 - "Community 102"
Cohesion: 1.0
Nodes (1): CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w

### Community 103 - "Community 103"
Cohesion: 1.0
Nodes (1): Static preambles for Orff prompt assembly — kept out of `prompt_service` so that

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): Indian RSS feed registry — adding a new outlet = one dict entry here, no other c

### Community 119 - "Community 119"
Cohesion: 1.0
Nodes (2): Anton app icon (rounded square, ascending orange bars + upward arrow), Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)

### Community 178 - "Community 178"
Cohesion: 1.0
Nodes (1): Strip query-string from URL for dedup purposes.

### Community 201 - "Community 201"
Cohesion: 1.0
Nodes (1): Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.  Run while logge

### Community 202 - "Community 202"
Cohesion: 1.0
Nodes (1): Compact preview: top-level keys + first list-of-dict path with sample.

### Community 203 - "Community 203"
Cohesion: 1.0
Nodes (1): The full metadata dict for a provider's model (defaults to its first model).

### Community 204 - "Community 204"
Cohesion: 1.0
Nodes (1): The `consumption` block for a model, with safe defaults if absent.

### Community 205 - "Community 205"
Cohesion: 1.0
Nodes (1): True when invoking this model costs real money (CostGuard gate).

### Community 206 - "Community 206"
Cohesion: 1.0
Nodes (1): The output-token cap an adapter should send for this model.

### Community 207 - "Community 207"
Cohesion: 1.0
Nodes (1): Real USD spend for a call from its prompt/completion token counts.

### Community 208 - "Community 208"
Cohesion: 1.0
Nodes (1): Resolved model choice from the frontend ModelPicker.      The frontend already a

### Community 209 - "Community 209"
Cohesion: 1.0
Nodes (1): The memory doc, or "" when none exists — additive, never blocks a chat.

### Community 210 - "Community 210"
Cohesion: 1.0
Nodes (1): Persist the doc into elgar (clipped to MAX_CHARS); returns what was stored.

### Community 211 - "Community 211"
Cohesion: 1.0
Nodes (1): Return (username, password) for UI probes — sourced from Wagner user credentials

### Community 212 - "Community 212"
Cohesion: 1.0
Nodes (1): Parse a stored session back into structured turns for resume (empty when absent)

### Community 213 - "Community 213"
Cohesion: 1.0
Nodes (1): Write a plan doc into the store; returns its `elgar://plan/<id>` ref.

### Community 214 - "Community 214"
Cohesion: 1.0
Nodes (1): Read a doc's content from the store; None when it does not exist.

### Community 215 - "Community 215"
Cohesion: 1.0
Nodes (1): Delete a doc from the store; True on success, False when it does not exist.

### Community 216 - "Community 216"
Cohesion: 1.0
Nodes (1): Parse a stored session back into structured turns for resume (empty when absent)

### Community 217 - "Community 217"
Cohesion: 1.0
Nodes (1): Write a plan doc into the store; returns its `elgar://plan/<id>` ref.

### Community 218 - "Community 218"
Cohesion: 1.0
Nodes (1): Read a doc's content from the store; None when it does not exist.

### Community 219 - "Community 219"
Cohesion: 1.0
Nodes (1): Resolved model choice from the frontend ModelPicker.      The frontend already a

### Community 220 - "Community 220"
Cohesion: 1.0
Nodes (1): Inject dev JWT + bypass boot screen, navigate to root.

### Community 221 - "Community 221"
Cohesion: 1.0
Nodes (1): Return True when the chat rail aside has pointer-events: auto (i.e. actually ope

### Community 222 - "Community 222"
Cohesion: 1.0
Nodes (1): Open the chat rail if not already interactive.

### Community 223 - "Community 223"
Cohesion: 1.0
Nodes (1): Raised when a paid provider is invoked without user confirmation.

### Community 224 - "Community 224"
Cohesion: 1.0
Nodes (1): Singleton guard; tracks which providers incur real cost.

### Community 225 - "Community 225"
Cohesion: 1.0
Nodes (1): Resolved model choice from the frontend ModelPicker.      The frontend already a

### Community 226 - "Community 226"
Cohesion: 1.0
Nodes (1): RateLimiter (token-bucket)

### Community 227 - "Community 227"
Cohesion: 1.0
Nodes (1): Cloud-Only Inference / Offline Behavior

### Community 228 - "Community 228"
Cohesion: 1.0
Nodes (1): Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)

## Ambiguous Edges - Review These
- `Probe (probes/ dev script)` → `boot_probes.py (health checks)`  [AMBIGUOUS]
  probes/PROBES_VS_CONNECTORS.md · relation: conceptually_related_to
- `BaseBroker / BrokerSource abstraction` → `BaseBroker / BrokerSource abstraction`  [AMBIGUOUS]
  docs/HOW.md · relation: conceptually_related_to

## Knowledge Gaps
- **560 isolated node(s):** `Portfolio filter probe — verifies asset-class chips, sort, PnL filter, and text`, `Capture screenshots of the terminal, portfolio, and preferences pages.  Attaches`, `Get a token from the API and stash it in localStorage so AuthGuard lets us in.`, `Plan API probe — verifies the /plans surface and its leak-safety.  Standalone (n`, `Attach to existing CDP Chrome, intercept Binance wallet XHRs.  Run while logged` (+555 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 32`** (12 nodes): `useAddTickerItem()`, `useAddWatchlistItem()`, `useDashboardBrief()`, `useDashboardRisk()`, `useDashboardStats()`, `useDashboardTicker()`, `useDashboardWatchlist()`, `useDeleteTickerItem()`, `useDeleteWatchlistItem()`, `TerminalStats.tsx`, `TerminalStats()`, `dashboard.query.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (6 nodes): `useAuthStore.ts`, `applyHeader()`, `errorMessage()`, `errorStatus()`, `requestPath()`, `skipRefreshRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (6 nodes): `fmtDateTime()`, `fmtTime()`, `Notification()`, `severityIcon()`, `Notification.tsx`, `notifications.icons.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (5 nodes): `checkMultiline()`, `handleFooterSubmit()`, `handleKeyDown()`, `handleModeChange()`, `AlphaBar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (5 nodes): `do_run_migrations()`, `Alembic env.py — async migration runner.`, `run_migrations_offline()`, `run_migrations_online()`, `env.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (3 nodes): `reduceEvent()`, `sanitizeContent()`, `chat.events.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (3 nodes): `TerminalTopBar.tsx`, `isActive()`, `TerminalTopBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (2 nodes): `Shared slowapi rate limiter instance.`, `limiter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 102`** (2 nodes): `broker_urls.py`, `CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 103`** (2 nodes): `prompt_text.py`, `Static preambles for Orff prompt assembly — kept out of `prompt_service` so that`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (2 nodes): `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`, `dashboard_seed.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (2 nodes): `Indian RSS feed registry — adding a new outlet = one dict entry here, no other c`, `rss_feeds.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 119`** (2 nodes): `Anton app icon (rounded square, ascending orange bars + upward arrow)`, `Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 178`** (1 nodes): `Strip query-string from URL for dedup purposes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 201`** (1 nodes): `Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.  Run while logge`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 202`** (1 nodes): `Compact preview: top-level keys + first list-of-dict path with sample.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 203`** (1 nodes): `The full metadata dict for a provider's model (defaults to its first model).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 204`** (1 nodes): `The `consumption` block for a model, with safe defaults if absent.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 205`** (1 nodes): `True when invoking this model costs real money (CostGuard gate).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 206`** (1 nodes): `The output-token cap an adapter should send for this model.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 207`** (1 nodes): `Real USD spend for a call from its prompt/completion token counts.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 208`** (1 nodes): `Resolved model choice from the frontend ModelPicker.      The frontend already a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 209`** (1 nodes): `The memory doc, or "" when none exists — additive, never blocks a chat.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 210`** (1 nodes): `Persist the doc into elgar (clipped to MAX_CHARS); returns what was stored.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 211`** (1 nodes): `Return (username, password) for UI probes — sourced from Wagner user credentials`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 212`** (1 nodes): `Parse a stored session back into structured turns for resume (empty when absent)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 213`** (1 nodes): `Write a plan doc into the store; returns its `elgar://plan/<id>` ref.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 214`** (1 nodes): `Read a doc's content from the store; None when it does not exist.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 215`** (1 nodes): `Delete a doc from the store; True on success, False when it does not exist.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 216`** (1 nodes): `Parse a stored session back into structured turns for resume (empty when absent)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 217`** (1 nodes): `Write a plan doc into the store; returns its `elgar://plan/<id>` ref.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 218`** (1 nodes): `Read a doc's content from the store; None when it does not exist.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 219`** (1 nodes): `Resolved model choice from the frontend ModelPicker.      The frontend already a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 220`** (1 nodes): `Inject dev JWT + bypass boot screen, navigate to root.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 221`** (1 nodes): `Return True when the chat rail aside has pointer-events: auto (i.e. actually ope`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 222`** (1 nodes): `Open the chat rail if not already interactive.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 223`** (1 nodes): `Raised when a paid provider is invoked without user confirmation.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 224`** (1 nodes): `Singleton guard; tracks which providers incur real cost.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 225`** (1 nodes): `Resolved model choice from the frontend ModelPicker.      The frontend already a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 226`** (1 nodes): `RateLimiter (token-bucket)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 227`** (1 nodes): `Cloud-Only Inference / Offline Behavior`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 228`** (1 nodes): `Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Probe (probes/ dev script)` and `boot_probes.py (health checks)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `BaseBroker / BrokerSource abstraction` and `BaseBroker / BrokerSource abstraction`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `get()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 25`, `Community 26`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `QueryType` connect `Community 0` to `Community 1`, `Community 4`, `Community 5`, `Community 8`, `Community 20`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `alphaforge-logger — Structured rotating-file + console logger.` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 172 inferred relationships involving `get()` (e.g. with `_fetch_holdings()` and `run()`) actually correct?**
  _`get()` has 172 INFERRED edges - model-reasoned connections that need verification._
- **Are the 116 inferred relationships involving `str` (e.g. with `run()` and `run()`) actually correct?**
  _`str` has 116 INFERRED edges - model-reasoned connections that need verification._