# Graph Report - anton  (2026-06-12)

## Corpus Check
- 373 files · ~1,978,334 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2214 nodes · 3607 edges · 73 communities detected
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 1297 edges (avg confidence: 0.74)
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
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 109|Community 109]]
- [[_COMMUNITY_Community 162|Community 162]]
- [[_COMMUNITY_Community 185|Community 185]]
- [[_COMMUNITY_Community 186|Community 186]]
- [[_COMMUNITY_Community 187|Community 187]]
- [[_COMMUNITY_Community 188|Community 188]]
- [[_COMMUNITY_Community 189|Community 189]]
- [[_COMMUNITY_Community 190|Community 190]]
- [[_COMMUNITY_Community 191|Community 191]]
- [[_COMMUNITY_Community 192|Community 192]]
- [[_COMMUNITY_Community 193|Community 193]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 138 edges
2. `alphaforge-logger — Structured rotating-file + console logger.` - 45 edges
3. `Message` - 43 edges
4. `QueryType` - 42 edges
5. `ProviderResponse` - 34 edges
6. `connect_existing_chrome()` - 33 edges
7. `BrokerSource` - 28 edges
8. `ToolSchema` - 26 edges
9. `ProviderHealth` - 26 edges
10. `HoldingsAggregator` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Tool ABC + ToolRegistry` --semantically_similar_to--> `domain_role.py filename grammar`  [INFERRED] [semantically similar]
  concierge/docs/compare/19-tool-calling.md → convention/python.md
- `Fux invariant probe — emits the holdings-vs-total context as JSON.  Wires the `h` --uses--> `HoldingsAggregator`  [INFERRED]
  probes/fux_totals_probe.py → /Users/arpitarya/my_programs/alpha-forge/backend/app/modules/brokers/aggregator.py
- `listApiKeys()` --calls--> `get()`  [INFERRED]
  frontend/src/modules/auth/auth.api.ts → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `listSessions()` --calls--> `get()`  [INFERRED]
  frontend/src/modules/auth/auth.api.ts → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `A percentages-only holdings block safe to place in any prompt.` --uses--> `QueryType`  [INFERRED]
  backend/app/modules/concierge/holdings_private.py → concierge/llm/src/alphaforge_anton_llm/types.py

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
Nodes (166): AngelOneSource, _holding_from_csv(), _holding_from_row(), Angel One holdings — BrokerSource impl over CDP browser fetch + on-disk cache., BrokerSource, Adapter for one holdings provider — override `fetch()`., dump_binance(), is_csv_fresh() (+158 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (84): ABC, default_model(), health(), NewsSource, ProviderAdapter, ProviderHealth, NewsSource abstract base class — the contract every source must implement., The provider's default model id — the first entry in `providers.json`. (+76 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (122): capture_angelone_cash(), _pick_cash(), Angel One — capture free-cash balance via CDP from the funds page.  Probe-confir, _to_float(), main(), Print Angel One free cash via CDP capture of /funds/v2/getRMSLimit.  Attaches to, _capture(), main() (+114 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (108): Angel One source, Binance source (crypto), Groww source, IndMoney source (US stocks), Ticker Tape source (digital gold), Zerodha Kite source, Zerodha Coin source (ETF/MF), Absolute imports + package public surface (+100 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (64): _inr_invested(), _inr_value(), AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell, _as_cash() (+56 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (87): Cloud vision (Gemini Flash) for images/PDFs, Nightly cross-session summary, Dependency injection + fakes, Explicit fact extraction table, Followup model inheritance, Intent-to-model routing, Per-module Jupyter notebooks, Offline-state UX (queue + auto-retry) (+79 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (73): dump_angelone(), is_csv_fresh(), live_csv_path(), main(), Angel One holdings CSV cache — fetches via CDP browser, caches to CSV.  TTL cont, _ttl(), write_csv(), clear_csv_cache() (+65 more)

### Community 7 - "Community 7"
Cohesion: 0.03
Nodes (82): Live Per-Query Fan-out over Polling Rationale, News Ingestion Decision, News Source Expansion Backlog, One-File NewsSource Extensibility Contract, StockTwits Source (proposed), Full Session-Cached Snapshot Rationale, Holdings Context Injection, Agentic Loop (Plan-Execute) (+74 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (51): BaseSettings, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang() (+43 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (60): HoldingsAggregator, _bin(), Bridge to the elgar plan store — subprocess, same pattern as `fux_bridge`.  Savi, Write a plan doc into the store; returns its `elgar://plan/<id>` ref., _run(), save(), slugify(), store_path() (+52 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (57): _resolve(), check(), main(), enforce_floor(), Private holdings disclosure + provider floor for Orff.  The chokepoint that lets, Resolve routing for a query, forcing a trusted provider when it is private., main(), Git-safety guard — the enforcement behind the plan-store rule.  Money documents (+49 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (26): BraveSource, Brave Search source — free 2k req/month, web search fallback., BseAnnouncementsSource, BSE corporate announcements — uses BSE's public JSON API (no auth required)., GnewsSource, gnews source — free tier, 100 req/day, India filter., build_all_sources(), NewsdataSource (+18 more)

### Community 12 - "Community 12"
Cohesion: 0.04
Nodes (26): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), IAM tables — users, refresh tokens, API keys, audit log.  Revision ID: a3c9f2e1b, upgrade(), AppShell(), downgrade(), Remove IAM tables — IAM is now owned by Wagner.  Revision ID: b3d6f8a2c9e1 Revis, Badge() (+18 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (38): Base, DashboardTickerItem, DashboardWatchlistItem, SQLAlchemy ORM models for the terminal dashboard feeds.  Single-user app: ticker, One symbol that scrolls in the global terminal ticker bar., One row in the terminal-side Watchlist panel., add_ticker(), add_watchlist() (+30 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (37): build_system(), Build the system prompt that constrains Orff to the Fux component vocabulary., _sig(), _vocab(), composable_errors(), narrow_registry(), check(), client_whitelist() (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (33): _broker_detail(), probe_backend(), probe_brokers(), probe_database(), probe_llm(), probe_vault(), System readiness probes used by /health/boot. Each probe returns a BootService s, BootReport (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (31): createApiKey(), encryptCredentials(), extendSession(), getLoginKey(), getMe(), _importPublicKey(), listApiKeys(), listSessions() (+23 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (37): boot_probes.py (health checks), Broker registry.py, CDP Chrome session on port 9299, Connector (BrokerSource subclass), Frontend data flow (component -> query -> transformer -> service), Gemini text-embedding-004 (768d), Backend layered architecture (routes -> service -> repo), @alphaforge/logger Node package (pino) (+29 more)

### Community 18 - "Community 18"
Cohesion: 0.07
Nodes (37): afbach Vault, AngelOne Broker, probes/<broker>_probe.py, Broker XHR Probe, Chrome DevTools Protocol (CDP), app.modules.brokers._cdp Module, CDP Port 9299, connect_existing_chrome Helper (+29 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (13): usePlan(), usePlanDrift(), useProjection(), useSavePlan(), useHoldings(), useResetSource(), useStartLogin(), useSubmitOtp() (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (18): NewsAggregator, NewsAggregator — fans out to all enabled sources in parallel, deduplicates., deduplicate(), Deduplication — URL-canonical + title-hash; keeps the most recent copy., Return items with duplicates removed, keeping the newest copy of each story., list_sources(), Search Indian market news across all enabled sources., Search news — POST variant for richer filters (since, symbol list). (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.1
Nodes (13): ChatProvider(), loadChoice(), ctxScore(), pickDefaultChoice(), score(), get_current_user(), FastAPI dependencies — shared across all route modules., Lightweight user object built from Wagner JWT claims — no DB round-trip. (+5 more)

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (23): Communities Legend (Community 0..30+ colored swatches), Node Info Panel (Click a node to inspect), Graphify Graph — Multi-Community Force Layout (F3), Distributed Blue Community Clusters, Fux Graph — Community Layout F4 (162 communities), Circular Ring Arrangement of Community Nodes around Central Hub, Fux Graph — Macro Ring Layout (162 communities, orange theme), Copy Governed Subgraph Button (+15 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (11): streamBootSync(), diagnose(), groupByReason(), reloadAction(), slugList(), truncate(), announce(), BootGate() (+3 more)

### Community 24 - "Community 24"
Cohesion: 0.12
Nodes (20): Highlighted node: health (~26 edges), Overview minimap, Fux Graph — Initial load (Communities lens, 163 communities), God node: get (function, 766 edges), Fux Graph — Node inspect (get function, 766 edges), Edge language legend (governs/references/calls/contains/related), Governance ledger panel (6 of 7048 edges), Lens panel (Knowledge/Communities, Heat/Path) (+12 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (13): createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Anton Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, get_logger(), Centralized logging configuration for AlphaForge Anton backend.  Thin wrapper ar, Configure and return the application root logger. (+5 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (18): Focused Function Node (broker module, 37 edges), Node Detail Tooltip (backend/app/modules/broker), Orange Edge Fan from Focused Node, Fux Graph — Communities Mode, Node Neighbourhood Focus, Dense Community Cluster (blue), Labeled Frontend Nodes (Chatbot.tsx, dashboard.routes.tsx), Overview Minimap, Fux Graph — Zoomed Community with Visible Labels (+10 more)

### Community 27 - "Community 27"
Cohesion: 0.2
Nodes (15): Free cash sitting inside a broker wallet (not deployed in holdings)., WalletBalance, cached_sync_cash(), load_cached_cash(), _path(), Shared on-disk CSV cache for broker free-cash balances.  One file, one row per b, Check CSV cache first; only call fetch_cash() if the cache is stale., Return cached WalletBalance if the row exists and is within TTL, else None. (+7 more)

### Community 28 - "Community 28"
Cohesion: 0.12
Nodes (17): Angel One Broker, CDP Chrome Session Capture, Groww Broker, INDmoney Broker, Ticker Tape Broker, Zerodha Broker, Alpha Chat, AlphaForge Anton (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.14
Nodes (14): SolarOrb component, Alpha Forge Hi-Fi.html design spec, ravel-ui / solar-ui design system, ThemeProvider + useTheme (data-theme/data-accent), solar-orb-ball Implementation Log, solar-orb-ball Plan, solar-orb-ball playground index.html, solar-orb-ball README (+6 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (8): clearNotifications(), defaultTtl(), dismissNotification(), emit(), nextId(), pushNotification(), useNotifications(), NotificationsHost()

### Community 31 - "Community 31"
Cohesion: 0.17
Nodes (2): useDashboardStats(), TerminalStats()

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (11): NewsAggregator, Deduplicator (URL-canonical + title-hash), NewsItem schema, NewsSource ABC, NewsSourceSettings ORM (Fernet-encrypted keys), RedditSource (asyncpraw), RssSource adapter (rss_feeds.yaml), News Module Plan (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.24
Nodes (11): Governance Ledger Panel (5 of 7048 edges), inr-normalization Governed Node, Labeled Backend Nodes (db.py, demo.py, dated_routes.py), Fux Graph — After Checks with Governance Ledger, Visible Subgraph Copied Toast, Copy Governed Subgraph Button, Governance Ledger Panel, Highlighted Governed Edges (orange) (+3 more)

### Community 34 - "Community 34"
Cohesion: 0.22
Nodes (11): Frontend file nodes (SessionGroup.tsx, ChatPanel.tsx, NodeProject.tsx, notifications.store.ts), Overview minimap, Fux Graph Default Dense Cluster View, Copy governance subgraph button, Governance ledger panel (jsr-normalization, day-pnl, holdings-sum-equals-total, portfolio-valuation), Fux Graph Hero with Governance Ledger, Scattered community clusters with governance edges, Fux Graph v2 with Ledger Collapsed (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.24
Nodes (10): Anton app icon (@3x) — rounded dark squircle, orange ascending bars + rising arrow, Anton app icon: rounded dark tile containing the ascending bar-and-arrow symbol, Anton app icon (PNG): rounded dark tile with ascending bar-and-arrow symbol, Anton lockup (@2x) — symbol + ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton lockup (@3x) — high-res symbol + gray ALPHA FORGE, light ANTON, orange TRADING TERMINAL, Anton Lockup — symbol + 'ALPHA FORGE / ANTON / TRADING TERMINAL' wordmark, Anton lockup (PNG): symbol plus ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton Symbol — orange gradient ascending bar chart with rising arrow (+2 more)

### Community 36 - "Community 36"
Cohesion: 0.36
Nodes (6): classifyIntent(), providerDefault(), resolveProviderAuto(), resolveTopAuto(), activeModelFor(), lookup()

### Community 37 - "Community 37"
Cohesion: 0.28
Nodes (4): aggregateAll(), aggregateSelected(), currencySymbol(), fmtMoneyShort()

### Community 38 - "Community 38"
Cohesion: 0.28
Nodes (4): available(), Per-provider token-bucket rate limiter., Refills `rate` tokens per second up to `capacity`., TokenBucket

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (7): _capture_gold_data(), _ensure_logged_in(), fetch_holdings_via_browser(), normalize_gold(), Ticker Tape — CDP login + digital-gold holdings fetch.  Confirmed endpoints (pro, Convert profile/v2 + price response into a single holding dict., _to_float()

### Community 40 - "Community 40"
Cohesion: 0.32
Nodes (4): extractDetail(), kindFromStatus(), toApiError(), shouldRetry()

### Community 41 - "Community 41"
Cohesion: 0.39
Nodes (5): assetClassCounts(), bucketOf(), equitySubOf(), isInvitReit(), isUSEquity()

### Community 42 - "Community 42"
Cohesion: 0.32
Nodes (8): health function node (convergeImpl, 26 edges), Fux Graph Macro Settled (health node, Communities lens), Edge language legend (governs, references, calls, contains, related), get function god node (766 edges), Fux Knowledge Graph Engine UI, Lens panel (Knowledge / Communities / Heat / Path), Node Types legend (function, code-file, class, narrative, memory, regulatory, formula, invariant, rule), Fux Graph Macro View (get god node)

### Community 43 - "Community 43"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 45 - "Community 45"
Cohesion: 0.4
Nodes (2): requestPath(), skipRefreshRetry()

### Community 46 - "Community 46"
Cohesion: 0.33
Nodes (2): Notification(), severityIcon()

### Community 47 - "Community 47"
Cohesion: 0.5
Nodes (2): handleFooterSubmit(), handleKeyDown()

### Community 48 - "Community 48"
Cohesion: 0.5
Nodes (2): handleKeyDown(), handleSubmit()

### Community 49 - "Community 49"
Cohesion: 0.4
Nodes (1): Alembic env.py — async migration runner.

### Community 50 - "Community 50"
Cohesion: 0.5
Nodes (3): dashboard ticker + watchlist items  Revision ID: 1d8f1014a7d4 Revises: 640eee61b, _table(), upgrade()

### Community 51 - "Community 51"
Cohesion: 0.5
Nodes (2): readPersisted(), writePersisted()

### Community 56 - "Community 56"
Cohesion: 0.83
Nodes (3): aspectRatio(), squarify(), worstAspect()

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): main(), _probe(), Probe every registered LLM provider once and print a one-line result each.

### Community 59 - "Community 59"
Cohesion: 0.67
Nodes (3): _forward(), iam_proxy(), IAM proxy — forwards all /iam/* requests to Wagner.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (2): isActive(), TerminalTopBar()

### Community 66 - "Community 66"
Cohesion: 0.67
Nodes (3): LLM Research Agent Plan, LLM Research Workspace Plan, Master Plan Index

### Community 67 - "Community 67"
Cohesion: 0.67
Nodes (3): Stylized 'A' monogram mark (orange gradient), AlphaForge brand logo (orange/grey 'A' monogram + ALPHA FORGE wordmark), ALPHA FORGE wordmark text

### Community 68 - "Community 68"
Cohesion: 0.67
Nodes (3): Backend Server :8000, Frontend Server :3000, just dev Command

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): Indian RSS feed registry — adding a new outlet = one dict entry here, no other c

### Community 109 - "Community 109"
Cohesion: 1.0
Nodes (2): Anton app icon (rounded square, ascending orange bars + upward arrow), Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)

### Community 162 - "Community 162"
Cohesion: 1.0
Nodes (1): Strip query-string from URL for dedup purposes.

### Community 185 - "Community 185"
Cohesion: 1.0
Nodes (1): Inject dev JWT + bypass boot screen, navigate to root.

### Community 186 - "Community 186"
Cohesion: 1.0
Nodes (1): Return True when the chat rail aside has pointer-events: auto (i.e. actually ope

### Community 187 - "Community 187"
Cohesion: 1.0
Nodes (1): Open the chat rail if not already interactive.

### Community 188 - "Community 188"
Cohesion: 1.0
Nodes (1): Raised when a paid provider is invoked without user confirmation.

### Community 189 - "Community 189"
Cohesion: 1.0
Nodes (1): Singleton guard; tracks which providers incur real cost.

### Community 190 - "Community 190"
Cohesion: 1.0
Nodes (1): Resolved model choice from the frontend ModelPicker.      The frontend already a

### Community 191 - "Community 191"
Cohesion: 1.0
Nodes (1): RateLimiter (token-bucket)

### Community 192 - "Community 192"
Cohesion: 1.0
Nodes (1): Cloud-Only Inference / Offline Behavior

### Community 193 - "Community 193"
Cohesion: 1.0
Nodes (1): Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)

## Ambiguous Edges - Review These
- `Probe (probes/ dev script)` → `boot_probes.py (health checks)`  [AMBIGUOUS]
  probes/PROBES_VS_CONNECTORS.md · relation: conceptually_related_to
- `BaseBroker / BrokerSource abstraction` → `BaseBroker / BrokerSource abstraction`  [AMBIGUOUS]
  docs/HOW.md · relation: conceptually_related_to

## Knowledge Gaps
- **461 isolated node(s):** `Portfolio filter probe — verifies asset-class chips, sort, PnL filter, and text`, `Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.  Run while logge`, `Compact preview: top-level keys + first list-of-dict path with sample.`, `Capture screenshots of the terminal, portfolio, and preferences pages.  Attaches`, `Get a token from the API and stash it in localStorage so AuthGuard lets us in.` (+456 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 31`** (12 nodes): `useAddTickerItem()`, `useAddWatchlistItem()`, `useDashboardBrief()`, `useDashboardRisk()`, `useDashboardStats()`, `useDashboardTicker()`, `useDashboardWatchlist()`, `useDeleteTickerItem()`, `useDeleteWatchlistItem()`, `TerminalStats.tsx`, `TerminalStats()`, `dashboard.query.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (6 nodes): `useAuthStore.ts`, `applyHeader()`, `errorMessage()`, `errorStatus()`, `requestPath()`, `skipRefreshRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (6 nodes): `fmtDateTime()`, `fmtTime()`, `Notification()`, `severityIcon()`, `Notification.tsx`, `notifications.icons.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (5 nodes): `checkMultiline()`, `handleFooterSubmit()`, `handleKeyDown()`, `handleModeChange()`, `AlphaBar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (5 nodes): `autoGrow()`, `handleKeyDown()`, `handleSubmit()`, `onKey()`, `ChatRail.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (5 nodes): `do_run_migrations()`, `Alembic env.py — async migration runner.`, `run_migrations_offline()`, `run_migrations_online()`, `env.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (5 nodes): `ThemeProvider.tsx`, `readPersisted()`, `ThemeProvider()`, `useTheme()`, `writePersisted()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (3 nodes): `TerminalTopBar.tsx`, `isActive()`, `TerminalTopBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (2 nodes): `Shared slowapi rate limiter instance.`, `limiter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (2 nodes): `broker_urls.py`, `CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (2 nodes): `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`, `dashboard_seed.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (2 nodes): `Indian RSS feed registry — adding a new outlet = one dict entry here, no other c`, `rss_feeds.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 109`** (2 nodes): `Anton app icon (rounded square, ascending orange bars + upward arrow)`, `Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 162`** (1 nodes): `Strip query-string from URL for dedup purposes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 185`** (1 nodes): `Inject dev JWT + bypass boot screen, navigate to root.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 186`** (1 nodes): `Return True when the chat rail aside has pointer-events: auto (i.e. actually ope`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 187`** (1 nodes): `Open the chat rail if not already interactive.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 188`** (1 nodes): `Raised when a paid provider is invoked without user confirmation.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 189`** (1 nodes): `Singleton guard; tracks which providers incur real cost.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 190`** (1 nodes): `Resolved model choice from the frontend ModelPicker.      The frontend already a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 191`** (1 nodes): `RateLimiter (token-bucket)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 192`** (1 nodes): `Cloud-Only Inference / Offline Behavior`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 193`** (1 nodes): `Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Probe (probes/ dev script)` and `boot_probes.py (health checks)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `BaseBroker / BrokerSource abstraction` and `BaseBroker / BrokerSource abstraction`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `get()` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 39`, `Community 8`, `Community 9`, `Community 10`, `Community 59`, `Community 12`, `Community 11`, `Community 14`, `Community 15`, `Community 16`, `Community 20`, `Community 21`, `Community 23`, `Community 27`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `QueryType` connect `Community 10` to `Community 0`, `Community 1`, `Community 9`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `Text()` connect `Community 12` to `Community 8`, `Community 15`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 136 inferred relationships involving `get()` (e.g. with `_fetch_holdings()` and `run()`) actually correct?**
  _`get()` has 136 INFERRED edges - model-reasoned connections that need verification._
- **Are the 101 inferred relationships involving `str` (e.g. with `run()` and `_shape_summary()`) actually correct?**
  _`str` has 101 INFERRED edges - model-reasoned connections that need verification._