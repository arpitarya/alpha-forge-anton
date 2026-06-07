# Graph Report - anton  (2026-06-07)

## Corpus Check
- 333 files · ~1,609,382 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1933 nodes · 3053 edges · 61 communities detected
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 1029 edges (avg confidence: 0.75)
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
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 149|Community 149]]
- [[_COMMUNITY_Community 170|Community 170]]
- [[_COMMUNITY_Community 171|Community 171]]
- [[_COMMUNITY_Community 172|Community 172]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 117 edges
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
- `listApiKeys()` --calls--> `get()`  [INFERRED]
  frontend/src/modules/auth/auth.api.ts → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `listSessions()` --calls--> `get()`  [INFERRED]
  frontend/src/modules/auth/auth.api.ts → /Users/arpitarya/my_programs/alpha-forge/backend/notebooks/portfolio_dev.py
- `MemoryService (RAG)` --semantically_similar_to--> `Multi-layer Long-term Memory`  [INFERRED] [semantically similar]
  backend/implement_memory.txt → concierge/docs/4-news-llm-architecture.md
- `Per-domain frontend module layout` --semantically_similar_to--> `Repository structure (backend/frontend/packages)`  [INFERRED] [semantically similar]
  convention/typescript.md → docs/architecture.md

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

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (145): AngelOneSource, _holding_from_csv(), _holding_from_row(), Angel One holdings — BrokerSource impl over CDP browser fetch + on-disk cache., BrokerSource, Adapter for one holdings provider — override `fetch()`., dump_binance(), is_csv_fresh() (+137 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (66): ABC, default_model(), health(), NewsSource, ProviderAdapter, ProviderHealth, NewsSource abstract base class — the contract every source must implement., next() (+58 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (111): capture_angelone_cash(), _pick_cash(), Angel One — capture free-cash balance via CDP from the funds page.  Probe-confir, _to_float(), main(), Print Angel One free cash via CDP capture of /funds/v2/getRMSLimit.  Attaches to, _capture(), main() (+103 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (108): Angel One source, Binance source (crypto), Groww source, IndMoney source (US stocks), Ticker Tape source (digital gold), Zerodha Kite source, Zerodha Coin source (ETF/MF), Absolute imports + package public surface (+100 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (76): Base, BaseModel, _broker_detail(), probe_backend(), probe_brokers(), probe_database(), probe_llm(), probe_vault() (+68 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (68): HoldingsAggregator, _inr_invested(), _inr_value(), AllocationSlice, Aggregator response dataclasses + default rebalance targets., RebalanceDrift, RebalanceSuggestion, TreemapCell (+60 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (87): Cloud vision (Gemini Flash) for images/PDFs, Nightly cross-session summary, Dependency injection + fakes, Explicit fact extraction table, Followup model inheritance, Intent-to-model routing, Per-module Jupyter notebooks, Offline-state UX (queue + auto-retry) (+79 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (39): BraveSource, Brave Search source — free 2k req/month, web search fallback., BseAnnouncementsSource, BSE corporate announcements — uses BSE's public JSON API (no auth required)., default_model(), GnewsSource, gnews source — free tier, 100 req/day, India filter., build_all_sources() (+31 more)

### Community 8 - "Community 8"
Cohesion: 0.03
Nodes (82): Live Per-Query Fan-out over Polling Rationale, News Ingestion Decision, News Source Expansion Backlog, One-File NewsSource Extensibility Contract, StockTwits Source (proposed), Full Session-Cached Snapshot Rationale, Holdings Context Injection, Agentic Loop (Plan-Execute) (+74 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (51): dump_angelone(), is_csv_fresh(), live_csv_path(), main(), Angel One holdings CSV cache — fetches via CDP browser, caches to CSV.  TTL cont, _ttl(), write_csv(), dump_groww() (+43 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (46): BaseSettings, Chunk, chunk_file(), _chunk_markdown(), _chunk_python(), _chunk_ts_like(), _chunk_window(), detect_lang() (+38 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (23): initial schema with pgvector memory  Revision ID: 640eee61bc50 Revises:  Create, upgrade(), IAM tables — users, refresh tokens, API keys, audit log.  Revision ID: a3c9f2e1b, upgrade(), AppShell(), downgrade(), Remove IAM tables — IAM is now owned by Wagner.  Revision ID: b3d6f8a2c9e1 Revis, Badge() (+15 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (41): clear_csv_cache(), dated_csv_path(), dump_dir(), is_csv_fresh(), live_csv_path(), Shared CSV-cache utilities for broker holdings dump modules., Delete the live CSV cache for slug. Returns True if a file was removed., Raise ValueError for oversized or missing-column CSV files. (+33 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (33): createApiKey(), encryptCredentials(), extendSession(), getLoginKey(), getMe(), _importPublicKey(), listApiKeys(), listSessions() (+25 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (37): boot_probes.py (health checks), Broker registry.py, CDP Chrome session on port 9299, Connector (BrokerSource subclass), Frontend data flow (component -> query -> transformer -> service), Gemini text-embedding-004 (768d), Backend layered architecture (routes -> service -> repo), @alphaforge/logger Node package (pino) (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (27): Analyze AI exposure action card, Midcap IT breakouts action card, Portfolio risk right now action card, Rebalance toward defensives action card, Alpha AI conversational assistant, Alpha Brief panel (market sentiment, risk alert, next action), Alpha chat input panel (send, newline, streaming), Confidence stat card (71.9% / 88.4%) (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (11): streamBootSync(), diagnose(), groupByReason(), reloadAction(), slugList(), truncate(), announce(), BootGate() (+3 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (22): AlphaForge Brand, Alpha Concierge / Conversation AI, Voice Input (Listening State), Gemini Flash Provider, Terminal Access Login Screen (After Logout), Alpha Conversation Modal (live-00-current), Alpha Conversation Modal (live-fix-00-state), Terminal Dashboard - Notification/Issue Time Check (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (5): useResetSource(), useStartLogin(), useSubmitOtp(), useSyncSource(), useSourceRow()

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (13): createLogger(), get_logger(), getLogger(), Centralized logging configuration for AlphaForge Anton Python services.  Usage::, Return a child logger under the given *namespace*.      Example::          logge, get_logger(), Centralized logging configuration for AlphaForge Anton backend.  Thin wrapper ar, Configure and return the application root logger. (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (18): Alpha Brief panel (Market Sentiment, Risk Alert, Next Action), Auto routing option (routes across all providers per query), '7 brokers synced' status toast, Chat send/newline controls with model routing label, 'Ask Alpha' chat input box, Thinking indicator (Auto - Gemini Flash), User message 'show my portfolio risk', Gemini models list (Auto-Gemini, Gemini Flash, Gemini 2.5 Pro) (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (15): Free cash sitting inside a broker wallet (not deployed in holdings)., WalletBalance, cached_sync_cash(), load_cached_cash(), _path(), Shared on-disk CSV cache for broker free-cash balances.  One file, one row per b, Check CSV cache first; only call fetch_cash() if the cache is stale., Return cached WalletBalance if the row exists and is within TTL, else None. (+7 more)

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (17): Angel One Broker, CDP Chrome Session Capture, Groww Broker, INDmoney Broker, Ticker Tape Broker, Zerodha Broker, Alpha Chat, AlphaForge Anton (+9 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (14): SolarOrb component, Alpha Forge Hi-Fi.html design spec, ravel-ui / solar-ui design system, ThemeProvider + useTheme (data-theme/data-accent), solar-orb-ball Implementation Log, solar-orb-ball Plan, solar-orb-ball playground index.html, solar-orb-ball README (+6 more)

### Community 24 - "Community 24"
Cohesion: 0.22
Nodes (8): clearNotifications(), defaultTtl(), dismissNotification(), emit(), nextId(), pushNotification(), useNotifications(), NotificationsHost()

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (2): useDashboardStats(), TerminalStats()

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (12): Quick action cards (Analyze AI exposure, Rebalance toward defensives, Portfolio risk, Midcap IT breakouts), Ask Alpha chat input with Send/Newline controls, Alpha Conversation AI chat modal, Live Fix - After (Alpha Conversation ready), Live Fix - Model Picker open (before), Gemini models panel (Gemini Flash, Gemini 2.5 Pro), Provider list (Auto, Gemini, Groq, Cerebras, Mistral, OpenRouter, HuggingFace, Claude), Routing footer (routing - Gemini / Gemini Flash, select) (+4 more)

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (9): _capture_holdings_via_reload(), _ensure_logged_in(), _extract_equity_holdings(), fetch_holdings_via_browser(), normalize(), Angel One — CDP login + holdings fetch via the authenticated browser context.  S, Drill into the superportfolio response to pull out HoldingDetail rows., Map a superportfolio HoldingDetail row to the shared dict shape. (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.2
Nodes (5): NewsAggregator, NewsAggregator — fans out to all enabled sources in parallel, deduplicates., deduplicate(), Deduplication — URL-canonical + title-hash; keeps the most recent copy., Return items with duplicates removed, keeping the newest copy of each story.

### Community 29 - "Community 29"
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
Cohesion: 0.33
Nodes (7): _capture_gold_data(), _ensure_logged_in(), fetch_holdings_via_browser(), normalize_gold(), Ticker Tape — CDP login + digital-gold holdings fetch.  Confirmed endpoints (pro, Convert profile/v2 + price response into a single holding dict., _to_float()

### Community 36 - "Community 36"
Cohesion: 0.32
Nodes (4): extractDetail(), kindFromStatus(), toApiError(), shouldRetry()

### Community 37 - "Community 37"
Cohesion: 0.39
Nodes (5): assetClassCounts(), bucketOf(), equitySubOf(), isInvitReit(), isUSEquity()

### Community 38 - "Community 38"
Cohesion: 0.25
Nodes (8): Access Terminal submit button, EMAIL input field, Login Page screen (Terminal Access), PASSWORD input field, Terminal Access login card (ALPHAFORGE branded), Stylized 'A' monogram mark (orange gradient), AlphaForge brand logo (orange/grey 'A' monogram + ALPHA FORGE wordmark), ALPHA FORGE wordmark text

### Community 39 - "Community 39"
Cohesion: 0.38
Nodes (4): resolveProviderAuto(), resolveTopAuto(), activeModelFor(), lookup()

### Community 40 - "Community 40"
Cohesion: 0.33
Nodes (3): readErr(), handleSyncAll(), onAfter()

### Community 42 - "Community 42"
Cohesion: 0.4
Nodes (2): requestPath(), skipRefreshRetry()

### Community 43 - "Community 43"
Cohesion: 0.33
Nodes (2): Notification(), severityIcon()

### Community 44 - "Community 44"
Cohesion: 0.5
Nodes (2): handleKeyDown(), handleSubmit()

### Community 45 - "Community 45"
Cohesion: 0.4
Nodes (1): Alembic env.py — async migration runner.

### Community 46 - "Community 46"
Cohesion: 0.5
Nodes (3): dashboard ticker + watchlist items  Revision ID: 1d8f1014a7d4 Revises: 640eee61b, _table(), upgrade()

### Community 47 - "Community 47"
Cohesion: 0.5
Nodes (2): readPersisted(), writePersisted()

### Community 53 - "Community 53"
Cohesion: 0.83
Nodes (3): aspectRatio(), squarify(), worstAspect()

### Community 55 - "Community 55"
Cohesion: 0.67
Nodes (3): main(), _probe(), Probe every registered LLM provider once and print a one-line result each.

### Community 56 - "Community 56"
Cohesion: 0.67
Nodes (3): _forward(), iam_proxy(), IAM proxy — forwards all /iam/* requests to Wagner.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (2): isActive(), TerminalTopBar()

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): LLM Research Agent Plan, LLM Research Workspace Plan, Master Plan Index

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Shared slowapi rate limiter instance.

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): Deterministic seed data for the terminal dashboard panels.  Replaced by real bro

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): Indian RSS feed registry — adding a new outlet = one dict entry here, no other c

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (2): Anton app icon (rounded square, ascending orange bars + upward arrow), Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)

### Community 149 - "Community 149"
Cohesion: 1.0
Nodes (1): Strip query-string from URL for dedup purposes.

### Community 170 - "Community 170"
Cohesion: 1.0
Nodes (1): RateLimiter (token-bucket)

### Community 171 - "Community 171"
Cohesion: 1.0
Nodes (1): Cloud-Only Inference / Offline Behavior

### Community 172 - "Community 172"
Cohesion: 1.0
Nodes (1): Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)

## Ambiguous Edges - Review These
- `BaseBroker / BrokerSource abstraction` → `BaseBroker / BrokerSource abstraction`  [AMBIGUOUS]
  docs/HOW.md · relation: conceptually_related_to
- `Probe (probes/ dev script)` → `boot_probes.py (health checks)`  [AMBIGUOUS]
  probes/PROBES_VS_CONNECTORS.md · relation: conceptually_related_to

## Knowledge Gaps
- **396 isolated node(s):** `Portfolio filter probe — verifies asset-class chips, sort, PnL filter, and text`, `Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.  Run while logge`, `Compact preview: top-level keys + first list-of-dict path with sample.`, `Capture screenshots of the terminal, portfolio, and preferences pages.  Attaches`, `Get a token from the API and stash it in localStorage so AuthGuard lets us in.` (+391 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 25`** (12 nodes): `useAddTickerItem()`, `useAddWatchlistItem()`, `useDashboardBrief()`, `useDashboardRisk()`, `useDashboardStats()`, `useDashboardTicker()`, `useDashboardWatchlist()`, `useDeleteTickerItem()`, `useDeleteWatchlistItem()`, `TerminalStats.tsx`, `TerminalStats()`, `dashboard.query.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (9 nodes): `ChatProvider()`, `loadChoice()`, `useChat()`, `ChatContext.tsx`, `useChatStream.ts`, `getToken()`, `nanoid()`, `sanitizeContent()`, `useChatStream()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (6 nodes): `useAuthStore.ts`, `applyHeader()`, `errorMessage()`, `errorStatus()`, `requestPath()`, `skipRefreshRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (6 nodes): `fmtDateTime()`, `fmtTime()`, `Notification()`, `severityIcon()`, `Notification.tsx`, `notifications.icons.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (5 nodes): `autoGrow()`, `handleKeyDown()`, `handleSubmit()`, `onKey()`, `ChatRail.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (5 nodes): `do_run_migrations()`, `Alembic env.py — async migration runner.`, `run_migrations_offline()`, `run_migrations_online()`, `env.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (5 nodes): `ThemeProvider.tsx`, `readPersisted()`, `ThemeProvider()`, `useTheme()`, `writePersisted()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (3 nodes): `TerminalTopBar.tsx`, `isActive()`, `TerminalTopBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (2 nodes): `Shared slowapi rate limiter instance.`, `limiter.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (2 nodes): `broker_urls.py`, `CDP trigger-page URLs and XHR needle strings for every broker adapter.  Import w`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (2 nodes): `Deterministic seed data for the terminal dashboard panels.  Replaced by real bro`, `dashboard_seed.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (2 nodes): `Indian RSS feed registry — adding a new outlet = one dict entry here, no other c`, `rss_feeds.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (2 nodes): `Anton app icon (rounded square, ascending orange bars + upward arrow)`, `Anton horizontal logo (ALPHA FORGE ANTON Trading Terminal, ascending bar+arrow mark)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 149`** (1 nodes): `Strip query-string from URL for dedup purposes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 170`** (1 nodes): `RateLimiter (token-bucket)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 171`** (1 nodes): `Cloud-Only Inference / Offline Behavior`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 172`** (1 nodes): `Anton brand symbol — ascending bar chart with upward arrow (orange gradient, flat style, 2x)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `BaseBroker / BrokerSource abstraction` and `BaseBroker / BrokerSource abstraction`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Probe (probes/ dev script)` and `boot_probes.py (health checks)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `get()` connect `Community 0` to `Community 1`, `Community 2`, `Community 35`, `Community 4`, `Community 5`, `Community 7`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 16`, `Community 21`, `Community 56`, `Community 27`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `Text()` connect `Community 11` to `Community 10`, `Community 4`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `alphaforge-logger — Structured rotating-file + console logger.` connect `Community 1` to `Community 0`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `get()` (e.g. with `_fetch_holdings()` and `run()`) actually correct?**
  _`get()` has 115 INFERRED edges - model-reasoned connections that need verification._
- **Are the 91 inferred relationships involving `str` (e.g. with `run()` and `_shape_summary()`) actually correct?**
  _`str` has 91 INFERRED edges - model-reasoned connections that need verification._