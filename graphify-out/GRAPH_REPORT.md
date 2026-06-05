# Graph Report - .  (2026-06-05)

## Corpus Check
- Large corpus: 449 files · ~571,404 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 1928 nodes · 3043 edges · 58 communities detected
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 1025 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Broker CDP Probes|Broker CDP Probes]]
- [[_COMMUNITY_Concierge AI Service|Concierge AI Service]]
- [[_COMMUNITY_Broker Capture + IAM Crypto|Broker Capture + IAM Crypto]]
- [[_COMMUNITY_Broker Source Registry|Broker Source Registry]]
- [[_COMMUNITY_Holdings Aggregator|Holdings Aggregator]]
- [[_COMMUNITY_Concierge Design Decisions|Concierge Design Decisions]]
- [[_COMMUNITY_Broker CSV Dumps|Broker CSV Dumps]]
- [[_COMMUNITY_NewsSearch Sources|News/Search Sources]]
- [[_COMMUNITY_News & Concierge Rationale|News & Concierge Rationale]]
- [[_COMMUNITY_Config & Chunking|Config & Chunking]]
- [[_COMMUNITY_Broker Source Impls|Broker Source Impls]]
- [[_COMMUNITY_Dashboard ORM Models|Dashboard ORM Models]]
- [[_COMMUNITY_DB Migrations & Shell|DB Migrations & Shell]]
- [[_COMMUNITY_Boot Health Probes|Boot Health Probes]]
- [[_COMMUNITY_System Architecture Map|System Architecture Map]]
- [[_COMMUNITY_Dashboard Action Cards|Dashboard Action Cards]]
- [[_COMMUNITY_Zerodha DumpInstruments|Zerodha Dump/Instruments]]
- [[_COMMUNITY_Broker HTTPSession Helpers|Broker HTTP/Session Helpers]]
- [[_COMMUNITY_Boot Sync Frontend|Boot Sync Frontend]]
- [[_COMMUNITY_UI Screens (brandvoice)|UI Screens (brand/voice)]]
- [[_COMMUNITY_Portfolio Query Hooks|Portfolio Query Hooks]]
- [[_COMMUNITY_Centralized Logging|Centralized Logging]]
- [[_COMMUNITY_Alpha Chat UI|Alpha Chat UI]]
- [[_COMMUNITY_Broker+Chat Concept Map|Broker+Chat Concept Map]]
- [[_COMMUNITY_Solar UI Design System|Solar UI Design System]]
- [[_COMMUNITY_Notification Store|Notification Store]]
- [[_COMMUNITY_Dashboard Query Hooks|Dashboard Query Hooks]]
- [[_COMMUNITY_Alpha Conversation UI|Alpha Conversation UI]]
- [[_COMMUNITY_News Aggregator|News Aggregator]]
- [[_COMMUNITY_News Module Design|News Module Design]]
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
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 146|Community 146]]
- [[_COMMUNITY_Community 167|Community 167]]
- [[_COMMUNITY_Community 168|Community 168]]
- [[_COMMUNITY_Community 169|Community 169]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 116 edges
2. `alphaforge-logger — Structured rotating-file + console logger.` - 44 edges
3. `Message` - 36 edges
4. `connect_existing_chrome()` - 32 edges
5. `ProviderResponse` - 31 edges
6. `BrokerSource` - 28 edges
7. `ProviderHealth` - 25 edges
8. `ToolSchema` - 24 edges
9. `ProviderAdapter` - 22 edges
10. `fetch_holdings_via_browser()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Tool ABC + ToolRegistry` --semantically_similar_to--> `domain_role.py filename grammar`  [INFERRED] [semantically similar]
  concierge/docs/compare/19-tool-calling.md → convention/python.md
- `MemoryService (RAG)` --semantically_similar_to--> `Multi-layer Long-term Memory`  [INFERRED] [semantically similar]
  backend/implement_memory.txt → concierge/docs/4-news-llm-architecture.md
- `Per-domain frontend module layout` --semantically_similar_to--> `Repository structure (backend/frontend/packages)`  [INFERRED] [semantically similar]
  convention/typescript.md → docs/architecture.md
- `Groww holdings — BrokerSource impl over CDP browser fetch + on-disk cache.  Auth` --uses--> `BrokerSource`  [INFERRED]
  /Users/arpitarya/my_programs/anton/backend/app/modules/brokers/groww/groww_source.py → /Users/arpitarya/my_programs/alpha-forge/backend/app/modules/brokers/base.py
- `_extract_assets()` --calls--> `get()`  [INFERRED]
  /Users/arpitarya/my_programs/anton/backend/app/modules/brokers/binance/binance_source_helper.py → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py

## Hyperedges (group relationships)
- **Concierge 8-Block Prompt Assembly** — 4_prompt_builder, 4_holdings_snapshot, 4_user_intent_document, 4_long_term_memory, 4_news_aggregator [EXTRACTED 0.90]
- **Broker Holdings Aggregation Pipeline** — implement_brokersource_abc, implement_broker_registry, implement_holdings_aggregator, brokers_cdp_session, brokers_unified_holding_shape [EXTRACTED 0.85]
- **Agentic Plan-Execute-Verify Chain** — 17_agentic_loop, 25_verifier_pass, plan_agent_loop, 21_search_web_tool [INFERRED 0.80]
- **Project-wide v1 constraints driving every comparison decision** — decision_zero_paid_v1, decision_no_local_models, decision_no_docker, constraint_macbook_air_16gb [EXTRACTED 1.00]
- **Multi-layer long-term memory architecture** — concept_rolling_session_summary, concept_cross_session_summary, concept_fact_extraction, option_anthropic_memory_tool [EXTRACTED 1.00]
- **Typed SSE streaming feeds reasoning trace + plan + tool events to UI** — concept_typed_sse_events, concept_reasoning_trace, concept_parallel_tool_exec, option_sse_fetch [EXTRACTED 1.00]
- **Fux subsumes graphify + memory + narrative docs** — concept_fux_engine, concept_graphify_graph, concept_doc_per_change [EXTRACTED 1.00]
- **Broker source → dump_utils CSV → portfolio aggregation** — module_brokers, concept_dump_utils, module_portfolio [EXTRACTED 1.00]
- **Authoring-pattern guides (guide/comparison/verdict-first)** — concept_guide_pattern, doc_comparison_guide, concept_verdict_first [INFERRED 0.80]
- **** — concept_probe, concept_connector_brokersource, concept_cdp_session_9299 [EXTRACTED 1.00]
- **** — concept_news_aggregator, concept_news_source_abc, concept_news_dedup [EXTRACTED 1.00]
- **** — concept_repo_context_mcp_server, concept_repo_chunks_table, concept_gemini_embedding_004 [EXTRACTED 1.00]

## Communities

### Community 0 - "Broker CDP Probes"
Cohesion: 0.02
Nodes (171): capture_angelone_cash(), main(), Print Angel One free cash via CDP capture of /funds/v2/getRMSLimit.  Attaches to, _capture(), main(), Attach to existing CDP Chrome, intercept Angel One portfolio + funds XHRs.  Run, Compact preview: top-level keys + first list-of-dict path with sample., _shape_summary() (+163 more)

### Community 1 - "Concierge AI Service"
Cohesion: 0.03
Nodes (74): ABC, default_model(), health(), NewsSource, ProviderAdapter, ProviderHealth, NewsSource abstract base class — the contract every source must implement., BaseModel (+66 more)

### Community 2 - "Broker Capture + IAM Crypto"
Cohesion: 0.03
Nodes (80): _pick_cash(), Angel One — capture free-cash balance via CDP from the funds page.  Probe-confir, _to_float(), _extract_equity_holdings(), Drill into the superportfolio response to pull out HoldingDetail rows., createApiKey(), encryptCredentials(), extendSession() (+72 more)

### Community 3 - "Broker Source Registry"
Cohesion: 0.02
Nodes (108): Angel One source, Binance source (crypto), Groww source, IndMoney source (US stocks), Ticker Tape source (digital gold), Zerodha Kite source, Zerodha Coin source (ETF/MF), Absolute imports + package public surface (+100 more)

### Community 4 - "Holdings Aggregator"
Cohesion: 0.04
Nodes (67): HoldingsAggregator, _inr_invested(), _inr_value(), AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell (+59 more)

### Community 5 - "Concierge Design Decisions"
Cohesion: 0.03
Nodes (87): Cloud vision (Gemini Flash) for images/PDFs, Nightly cross-session summary, Dependency injection + fakes, Explicit fact extraction table, Followup model inheritance, Intent-to-model routing, Per-module Jupyter notebooks, Offline-state UX (queue + auto-retry) (+79 more)

### Community 6 - "Broker CSV Dumps"
Cohesion: 0.04
Nodes (71): dump_angelone(), is_csv_fresh(), live_csv_path(), main(), Angel One holdings CSV cache — fetches via CDP browser, caches to CSV.  TTL cont, _ttl(), write_csv(), clear_csv_cache() (+63 more)

### Community 7 - "News/Search Sources"
Cohesion: 0.03
Nodes (40): BraveSource, Brave Search source — free 2k req/month, web search fallback., BseAnnouncementsSource, BSE corporate announcements — uses BSE's public JSON API (no auth required)., default_model(), GnewsSource, gnews source — free tier, 100 req/day, India filter., build_all_sources() (+32 more)

### Community 8 - "News & Concierge Rationale"
Cohesion: 0.03
Nodes (82): Live Per-Query Fan-out over Polling Rationale, News Ingestion Decision, News Source Expansion Backlog, One-File NewsSource Extensibility Contract, StockTwits Source (proposed), Full Session-Cached Snapshot Rationale, Holdings Context Injection, Agentic Loop (Plan-Execute) (+74 more)

### Community 9 - "Config & Chunking"
Cohesion: 0.04
Nodes (51): BaseSettings, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang() (+43 more)

### Community 10 - "Broker Source Impls"
Cohesion: 0.05
Nodes (45): AngelOneSource, Angel One holdings — BrokerSource impl over CDP browser fetch + on-disk cache., BrokerSource, Adapter for one holdings provider — override `fetch()`., BinanceSource, Binance spot-wallet holdings — BrokerSource over CDP browser fetch (USD/USDT)., Vault-aware env helpers shared by all broker source helpers.  Two public helpers, Return True when every required key is set; log a vault hint if not. (+37 more)

### Community 11 - "Dashboard ORM Models"
Cohesion: 0.06
Nodes (38): Base, DashboardTickerItem, DashboardWatchlistItem, SQLAlchemy ORM models for the terminal dashboard feeds.  Single-user app: ticker, One symbol that scrolls in the global terminal ticker bar., One row in the terminal-side Watchlist panel., add_ticker(), add_watchlist() (+30 more)

### Community 12 - "DB Migrations & Shell"
Cohesion: 0.04
Nodes (23): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), IAM tables — users, refresh tokens, API keys, audit log.  Revision ID: a3c9f2e1b, upgrade(), AppShell(), downgrade(), Remove IAM tables — IAM is now owned by Wagner.  Revision ID: b3d6f8a2c9e1 Revis, Badge() (+15 more)

### Community 13 - "Boot Health Probes"
Cohesion: 0.08
Nodes (33): _broker_detail(), probe_backend(), probe_brokers(), probe_database(), probe_llm(), probe_vault(), System readiness probes used by /health/boot. Each probe returns a BootService s, BootReport (+25 more)

### Community 14 - "System Architecture Map"
Cohesion: 0.06
Nodes (37): boot_probes.py (health checks), Broker registry.py, CDP Chrome session on port 9299, Connector (BrokerSource subclass), Frontend data flow (component -> query -> transformer -> service), Gemini text-embedding-004 (768d), Backend layered architecture (routes -> service -> repo), @alphaforge/logger Node package (pino) (+29 more)

### Community 15 - "Dashboard Action Cards"
Cohesion: 0.11
Nodes (27): Analyze AI exposure action card, Midcap IT breakouts action card, Portfolio risk right now action card, Rebalance toward defensives action card, Alpha AI conversational assistant, Alpha Brief panel (market sentiment, risk alert, next action), Alpha chat input panel (send, newline, streaming), Confidence stat card (71.9% / 88.4%) (+19 more)

### Community 16 - "Zerodha Dump/Instruments"
Cohesion: 0.15
Nodes (21): dump_zerodha(), is_csv_fresh(), live_csv_path(), main(), Zerodha holdings CSV cache — fetches via CDP, caches to CSV.  TTL controlled by, _ttl(), write_csv(), _cache_path() (+13 more)

### Community 17 - "Broker HTTP/Session Helpers"
Cohesion: 0.11
Nodes (18): _cache_root(), _check_dev_host(), clear_session(), _fernet(), load_session(), make_client(), Shared httpx client factory + a tiny on-disk JSON cache for session tokens.  Bro, Raise RuntimeError if base_url is not on the approved list in dev mode. (+10 more)

### Community 18 - "Boot Sync Frontend"
Cohesion: 0.12
Nodes (11): streamBootSync(), diagnose(), groupByReason(), reloadAction(), slugList(), truncate(), announce(), BootGate() (+3 more)

### Community 19 - "UI Screens (brand/voice)"
Cohesion: 0.16
Nodes (22): AlphaForge Brand, Alpha Concierge / Conversation AI, Voice Input (Listening State), Gemini Flash Provider, Terminal Access Login Screen (After Logout), Alpha Conversation Modal (live-00-current), Alpha Conversation Modal (live-fix-00-state), Terminal Dashboard - Notification/Issue Time Check (+14 more)

### Community 20 - "Portfolio Query Hooks"
Cohesion: 0.13
Nodes (5): useResetSource(), useStartLogin(), useSubmitOtp(), useSyncSource(), useSourceRow()

### Community 21 - "Centralized Logging"
Cohesion: 0.12
Nodes (13): createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Anton Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, get_logger(), Centralized logging configuration for AlphaForge Anton backend.  Thin wrapper ar, Configure and return the application root logger. (+5 more)

### Community 22 - "Alpha Chat UI"
Cohesion: 0.12
Nodes (18): Alpha Brief panel (Market Sentiment, Risk Alert, Next Action), Auto routing option (routes across all providers per query), '7 brokers synced' status toast, Chat send/newline controls with model routing label, 'Ask Alpha' chat input box, Thinking indicator (Auto - Gemini Flash), User message 'show my portfolio risk', Gemini models list (Auto-Gemini, Gemini Flash, Gemini 2.5 Pro) (+10 more)

### Community 23 - "Broker+Chat Concept Map"
Cohesion: 0.12
Nodes (17): Angel One Broker, CDP Chrome Session Capture, Groww Broker, INDmoney Broker, Ticker Tape Broker, Zerodha Broker, Alpha Chat, AlphaForge Anton (+9 more)

### Community 24 - "Solar UI Design System"
Cohesion: 0.14
Nodes (14): SolarOrb component, Alpha Forge Hi-Fi.html design spec, ravel-ui / solar-ui design system, ThemeProvider + useTheme (data-theme/data-accent), solar-orb-ball Implementation Log, solar-orb-ball Plan, solar-orb-ball playground index.html, solar-orb-ball README (+6 more)

### Community 25 - "Notification Store"
Cohesion: 0.22
Nodes (8): clearNotifications(), defaultTtl(), dismissNotification(), emit(), nextId(), pushNotification(), useNotifications(), NotificationsHost()

### Community 26 - "Dashboard Query Hooks"
Cohesion: 0.17
Nodes (2): useDashboardStats(), TerminalStats()

### Community 27 - "Alpha Conversation UI"
Cohesion: 0.18
Nodes (12): Quick action cards (Analyze AI exposure, Rebalance toward defensives, Portfolio risk, Midcap IT breakouts), Ask Alpha chat input with Send/Newline controls, Alpha Conversation AI chat modal, Live Fix - After (Alpha Conversation ready), Live Fix - Model Picker open (before), Gemini models panel (Gemini Flash, Gemini 2.5 Pro), Provider list (Auto, Gemini, Groq, Cerebras, Mistral, OpenRouter, HuggingFace, Claude), Routing footer (routing - Gemini / Gemini Flash, select) (+4 more)

### Community 28 - "News Aggregator"
Cohesion: 0.2
Nodes (5): NewsAggregator, NewsAggregator — fans out to all enabled sources in parallel, deduplicates., deduplicate(), Deduplication — URL-canonical + title-hash; keeps the most recent copy., Return items with duplicates removed, keeping the newest copy of each story.

### Community 29 - "News Module Design"
Cohesion: 0.18
Nodes (11): NewsAggregator, Deduplicator (URL-canonical + title-hash), NewsItem schema, NewsSource ABC, NewsSourceSettings ORM (Fernet-encrypted keys), RedditSource (asyncpraw), RssSource adapter (rss_feeds.yaml), News Module Plan (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.24
Nodes (7): get_current_user(), FastAPI dependencies — shared across all route modules., Lightweight user object built from Wagner JWT claims — no DB round-trip., user_from_jwt(), UserClaims, decode_access_token(), Security utilities — JWT token validation.

### Community 31 - "Community 31"
Cohesion: 0.24
Nodes (10): Anton app icon (@3x) — rounded dark squircle, orange ascending bars + rising arrow, Anton app icon: rounded dark tile containing the ascending bar-and-arrow symbol, Anton app icon (PNG): rounded dark tile with ascending bar-and-arrow symbol, Anton lockup (@2x) — symbol + ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton lockup (@3x) — high-res symbol + gray ALPHA FORGE, light ANTON, orange TRADING TERMINAL, Anton Lockup — symbol + 'ALPHA FORGE / ANTON / TRADING TERMINAL' wordmark, Anton lockup (PNG): symbol plus ALPHA FORGE / ANTON / TRADING TERMINAL wordmark, Anton Symbol — orange gradient ascending bar chart with rising arrow (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (2): ChatProvider(), useChatStream()

### Community 33 - "Community 33"
Cohesion: 0.28
Nodes (4): aggregateAll(), aggregateSelected(), currencySymbol(), fmtMoneyShort()

### Community 34 - "Community 34"
Cohesion: 0.28
Nodes (4): available(), Per-provider token-bucket rate limiter., Refills `rate` tokens per second up to `capacity`., TokenBucket

### Community 35 - "Community 35"
Cohesion: 0.32
Nodes (4): extractDetail(), kindFromStatus(), toApiError(), shouldRetry()

### Community 36 - "Community 36"
Cohesion: 0.39
Nodes (5): assetClassCounts(), bucketOf(), equitySubOf(), isInvitReit(), isUSEquity()

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (8): Access Terminal submit button, EMAIL input field, Login Page screen (Terminal Access), PASSWORD input field, Terminal Access login card (ALPHAFORGE branded), Stylized 'A' monogram mark (orange gradient), AlphaForge brand logo (orange/grey 'A' monogram + ALPHA FORGE wordmark), ALPHA FORGE wordmark text

### Community 38 - "Community 38"
Cohesion: 0.38
Nodes (4): resolveProviderAuto(), resolveTopAuto(), activeModelFor(), lookup()

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 41 - "Community 41"
Cohesion: 0.4
Nodes (2): requestPath(), skipRefreshRetry()

### Community 42 - "Community 42"
Cohesion: 0.33
Nodes (2): Notification(), severityIcon()

### Community 43 - "Community 43"
Cohesion: 0.5
Nodes (2): handleKeyDown(), handleSubmit()

### Community 44 - "Community 44"
Cohesion: 0.4
Nodes (1): Alembic env.py — async migration runner.

### Community 45 - "Community 45"
Cohesion: 0.5
Nodes (3): dashboard ticker + watchlist items  Revision ID: 1d8f1014a7d4 Revises: 640eee61b, _table(), upgrade()

### Community 46 - "Community 46"
Cohesion: 0.5
Nodes (2): readPersisted(), writePersisted()

### Community 52 - "Community 52"
Cohesion: 0.83
Nodes (3): aspectRatio(), squarify(), worstAspect()

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (2): isActive(), TerminalTopBar()

### Community 60 - "Community 60"
Cohesion: 0.67
Nodes (3): LLM Research Agent Plan, LLM Research Workspace Plan, Master Plan Index

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Indian RSS feed registry — adding a new outlet = one dict entry here, no other c

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (2): Anton app icon (rounded square, ascending orange bars + upward arrow), Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)

### Community 146 - "Community 146"
Cohesion: 1.0
Nodes (1): Strip query-string from URL for dedup purposes.

### Community 167 - "Community 167"
Cohesion: 1.0
Nodes (1): RateLimiter (token-bucket)

### Community 168 - "Community 168"
Cohesion: 1.0
Nodes (1): Cloud-Only Inference / Offline Behavior

### Community 169 - "Community 169"
Cohesion: 1.0
Nodes (1): Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)

## Ambiguous Edges - Review These
- `BaseBroker / BrokerSource abstraction` → `BaseBroker / BrokerSource abstraction`  [AMBIGUOUS]
  docs/HOW.md · relation: conceptually_related_to
- `Probe (probes/ dev script)` → `boot_probes.py (health checks)`  [AMBIGUOUS]
  /Users/arpitarya/my_programs/anton/probes/PROBES_VS_CONNECTORS.md · relation: conceptually_related_to

## Knowledge Gaps
- **395 isolated node(s):** `Portfolio filter probe — verifies asset-class chips, sort, PnL filter, and text`, `Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.  Run while logge`, `Compact preview: top-level keys + first list-of-dict path with sample.`, `Capture screenshots of the terminal, portfolio, and preferences pages.  Attaches`, `Get a token from the API and stash it in localStorage so AuthGuard lets us in.` (+390 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Dashboard Query Hooks`** (12 nodes): `useAddTickerItem()`, `useAddWatchlistItem()`, `useDashboardBrief()`, `useDashboardRisk()`, `useDashboardStats()`, `useDashboardTicker()`, `useDashboardWatchlist()`, `useDeleteTickerItem()`, `useDeleteWatchlistItem()`, `TerminalStats.tsx`, `TerminalStats()`, `dashboard.query.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (9 nodes): `ChatProvider()`, `loadChoice()`, `useChat()`, `ChatContext.tsx`, `useChatStream.ts`, `getToken()`, `nanoid()`, `sanitizeContent()`, `useChatStream()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (6 nodes): `useAuthStore.ts`, `applyHeader()`, `errorMessage()`, `errorStatus()`, `requestPath()`, `skipRefreshRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (6 nodes): `fmtDateTime()`, `fmtTime()`, `Notification()`, `severityIcon()`, `Notification.tsx`, `notifications.icons.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (5 nodes): `autoGrow()`, `handleKeyDown()`, `handleSubmit()`, `onKey()`, `ChatRail.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (5 nodes): `do_run_migrations()`, `Alembic env.py — async migration runner.`, `run_migrations_offline()`, `run_migrations_online()`, `env.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (5 nodes): `ThemeProvider.tsx`, `readPersisted()`, `ThemeProvider()`, `useTheme()`, `writePersisted()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (3 nodes): `TerminalTopBar.tsx`, `isActive()`, `TerminalTopBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (2 nodes): `Shared slowapi rate limiter instance.`, `limiter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (2 nodes): `broker_urls.py`, `CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (2 nodes): `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`, `dashboard_seed.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (2 nodes): `Indian RSS feed registry — adding a new outlet = one dict entry here, no other c`, `rss_feeds.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (2 nodes): `Anton app icon (rounded square, ascending orange bars + upward arrow)`, `Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 146`** (1 nodes): `Strip query-string from URL for dedup purposes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 167`** (1 nodes): `RateLimiter (token-bucket)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 168`** (1 nodes): `Cloud-Only Inference / Offline Behavior`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 169`** (1 nodes): `Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `BaseBroker / BrokerSource abstraction` and `BaseBroker / BrokerSource abstraction`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Probe (probes/ dev script)` and `boot_probes.py (health checks)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `get()` connect `Broker Capture + IAM Crypto` to `Broker CDP Probes`, `Concierge AI Service`, `Holdings Aggregator`, `Broker CSV Dumps`, `News/Search Sources`, `Config & Chunking`, `Broker Source Impls`, `DB Migrations & Shell`, `Boot Health Probes`, `Zerodha Dump/Instruments`, `Broker HTTP/Session Helpers`, `Boot Sync Frontend`, `News Aggregator`, `Community 30`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `alphaforge-logger — Structured rotating-file + console logger.` connect `Concierge AI Service` to `Broker Source Impls`, `Holdings Aggregator`, `News/Search Sources`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `Text()` connect `DB Migrations & Shell` to `Config & Chunking`, `Boot Health Probes`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 114 inferred relationships involving `get()` (e.g. with `_fetch_holdings()` and `run()`) actually correct?**
  _`get()` has 114 INFERRED edges - model-reasoned connections that need verification._
- **Are the 90 inferred relationships involving `str` (e.g. with `run()` and `_shape_summary()`) actually correct?**
  _`str` has 90 INFERRED edges - model-reasoned connections that need verification._