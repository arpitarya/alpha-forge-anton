# AlphaForge Anton — Architecture & Key Files

## Project

**AlphaForge Anton** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Built for personal use — not a SaaS product. Self-hosted, open-source, MIT licensed.

## Repository Structure

```
alpha-forge-anton/
├── backend/          Python 3.14 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt, env_loader
│   ├── app/modules/  Feature modules — each owns its routes/service/models
│   │   ├── health/      /api/v1/* health endpoint
│   │   ├── iam/         Wagner IAM proxy — forwards /api/v1/iam/* to Wagner service on :8001
│   │   ├── portfolio/   routes + Holding/Order/Watchlist ORM
│   │   ├── plans/       plan store plane — plan_loader (reads the private elgar store at ELGAR_DIR), plan_drift (targets × live actuals, %-only), /plans + /plans/drift routes. Money docs live in elgar (sibling tool, ~/my_programs/elgar), never in this repo — `fux why plan-store`
│   │   ├── brokers/     pluggable BrokerSource adapters (Zerodha Kite/Coin, Groww, Angel One, IndMoney, TickerTape, Binance) + aggregator + registry. Used by portfolio routes. All CSV portfolio dumps share `dump_utils.py` — see broker-csv-dumps.md
│   │   ├── trade/       routes (paper/live trade endpoints)
│   │   ├── signals/     deterministic swing-trade engine — strategy_config (tunable knobs, Orff-editable) + quote_source (yfinance, cached) + indicators (ta-lib) + signal_rules + universe/screener_rules + plan_store/plan_diff (re-plan loop, elgar actions/) + strategy_tuning (ApprovalCard→elgar) + plan_card (deterministic UISpec) + weekly_service (scheduled review) + pnl_tracker (realized P&L net of brokerage/STT/friction/STCG). GET /signals/review (plan+diff) /screen /strategy /weekly · POST /plan /strategy /pnl. No LLM in the numbers — see docs/signals.md
│   │   ├── edges/       edge-discovery engine — pre-registered hypotheses through gates 1–2 + journal (elgar), trial_ledger (append-only counts-only trial-budget integrity) + null_selftest (random-data trust check). **EB-0 cross-sectional factor edge**: factor_{schema,panel,rank,quality,trend,exits,rebalance} (12-1 momentum + quality + NIFTY-trend → weekly net-return series) → funnel (Gates 1-3: cscv_pbo + deflated_sharpe + harvey_liu + factor_walkforward + gate3_montecarlo + scenario_library) → signed contracts.TestReport; eb0_cli = `just eb0`. Deterministic, offline, $0. See docs/edges.md
│   │   ├── contracts/   Phase-0 engine↔UI contracts (single source of truth) — Objective/TestReport/Cone/ApprovalProposal/DecisionRow/FeedState Pydantic models + contracts_codegen → generated frontend TS types (drift-tested). See docs/contracts.md
│   │   ├── marketdata/  Gate-0 data integrity — NSE bhavcopy ingest (reuses dump_utils I/O, own OHLCV columns) + point-in-time universe + gate0_integrity (rejects look-ahead / survivorship leakage). See docs/edges.md
│   │   ├── funding/     fixed-cost opex registry — subscriptions.toml ($0, no secrets) → opex_per_month(), the denominator of Objective.self_funding. `covered` is honest-pending until a realised-P&L source exists (Gate-4 paper); cage savings reduce opex, not income. See docs/cage.md
│   │   └── dashboard/   routes (cross-module aggregation)
│   ├── app/main.py   FastAPI app factory; mounts api_router from app.modules
│   ├── alembic/      Database migrations
│   └── tests/        Pytest suite
├── packages/
│   ├── logger-py/    Publishable Python logger package (alphaforge-logger)
│   │   └── src/alphaforge_logger/  setup_logging(), get_logger()
│   ├── logger-node/  Publishable Node/TS logger package (@alphaforge/logger)
│   │   └── src/      createLogger(), getLogger() — pino-based
│   └── solar-ui/ Publishable UI component library (@alphaforge-anton/solar-ui)
│       ├── src/components/  Button, Input, Card, Badge, Icon, Text, SearchBox, PrefRow, PrefGroup, PrefControls + finance-composition primitives (LineChart, DonutChart, AllocationBar, DataTable, DeltaText, StatGrid — Orff-composable, see ui-component-contract)
│       └── src/styles/      fonts.css, theme.css, base.css (design tokens + base styles)
├── frontend/         Next.js 15 (App Router) + React 19 + TypeScript + Tailwind v4
│   ├── src/app/      Pages and layouts (Solar Terminal theme)
│   ├── src/lib/      Cross-cutting infra: `api.ts` (axios client), `logger.ts`, `providers.tsx`, `store.ts`
│   └── src/modules/  Feature modules — mirrors backend/app/modules layout
│       ├── portfolio/   portfolio.{api,query,types}.ts + components (Ledger, Treemap, SourcesPanel, ...)
│       ├── plans/       plans.{api,query,types}.ts — /plans client: plan, drift, projection, save-to-elgar
│       ├── concierge/   Orff chat (ChatRail, AlphaBar) + composed UI: SpecCard/SpecHost render Fux-validated UISpecs from the chat stream; compose.registry.ts is the client whitelist (mirror of backend COMPOSABLE_COMPONENTS); SavePlanButton → POST /plans → elgar store. Track-U live surface: GuardrailStrip (pinned read-only objective) + inline ConeCard/ProposalCard/GroundedAnswer/FeedToggle via the /proposal demo. See docs/track-u-ui.md
│       ├── goals/        Track-U editable north-star (/goals) — GoalsPanel (Calmar hero + drawdown guard + self-funding + collapsed capital-structure) + GoalsAside; Phase-0 Objective on mock
│       ├── decisions/    Track-U replayable prove-it ledger (/decisions) — DecisionsLedger + CalibrationSummary (13·4·3) + DecisionRowCard (proposal→downside→decision→outcome + REPLAY); Phase-0 DecisionRow on mock
│       ├── forge/        Track-U shared Hi-Fi primitives — Num, UChip, FanChart (+fan.utils), Www. Styling in src/app/forge-*.css (.of-* classes, tokens inherited from theme.css)
│       ├── ai/          ai.{api,query}.ts + AIChat
│       ├── trade/       trade.{api,query}.ts
│       ├── screener/    ScreenerPanel (hardcoded stub — no live API)
│       ├── dashboard/   dashboard.{api,query,types}.ts + terminal-home components
│       └── auth/        auth.api.ts (IAM client), auth.types.ts, useAuthStore.ts, auth.guard.tsx
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── repo-context-mcp/ Tool-agnostic MCP server — gives Claude/Copilot/Cursor/any MCP client semantic + structural context over this repo
│   └── src/alphaforge_anton_repo_context/  server, indexer, chunker, embeddings, watcher, tools/
├── docs/             WHY.md, WHAT.md, HOW.md, GETTING_STARTED.md + canonical shared docs for AI agents
└── design/           Design system & Gemini Stitch tokens
```

## Tech Decisions

| Area | Choice | Notes |
|------|--------|-------|
| Python pkg mgr | uv (workspace) | Single `uv.lock` at repo root; members declared in `[tool.uv.workspace]`. One `.venv/` shared across backend, screener, logger-py |
| Python version | pyenv | Pinned in `.python-version` (3.14.2) |
| Node pkg mgr | pnpm | Lockfile: `pnpm-lock.yaml`; config in `.npmrc` |
| Node version | nvm | Pinned in `.nvmrc` |
| Monorepo | pnpm workspaces | `pnpm-workspace.yaml` at root; `packages/*` + `frontend` |
| UI library | @alphaforge-anton/solar-ui | Publishable package built with tsup (ESM + CJS + DTS) |
| Logging (Python) | alphaforge-logger | Rotating file + console, env-configurable |
| Logging (Node) | @alphaforge/logger | Pino-based, file + console, publishable tsup pkg |
| DB | PostgreSQL 16 | Async via asyncpg + SQLAlchemy |
| Cache | Redis 7 | Quotes cache, pub/sub, Celery broker |
| AI | OpenAI + LangChain | RAG with market data context |
| Repo Context MCP | alphaforge-anton-repo-context-mcp | Local stdio MCP server; pgvector-backed semantic + structural repo context for Claude/Copilot/Cursor/any MCP client |
| Brokers | Abstract BrokerSource interface | Zerodha first, then Groww, Angel One, Upstox |
| Auth (IAM) | Wagner (standalone service on `:8001`) | JWT + rotating refresh tokens + `wgr_` API keys; owner/viewer roles; audit log. Anton proxies `/api/v1/iam/*` → Wagner; validates JWTs locally from claims (no DB round-trip). Data lives in Wagner's SQLite (`wagner/backend/wagner.db`). |
| Security | Dante (`alphaforge-dante`) | Log redaction (`redactor`), IP allowlist middleware (`warden`), path guard (`curator`), failed-login tracking (`watchman`), zero-trust egress (`gateway`), posture step-up (`posture`), honeypot (`inferno`). Run `just dante-audit` for SAST+CVE+license |
| Local infra | brew services (Postgres, Redis) | Containers optional via OrbStack |
| CI infra | devcontainer.json | GitHub Codespaces compatible |

## Key Files

### Backend
- `backend/app/main.py` — FastAPI app factory; mounts Dante `warden` middleware after CORS
- `backend/app/core/config.py` — All environment variables; `wagner_url` points to the Wagner IAM service
- `backend/app/core/security.py` — JWT decode only (`decode_access_token → dict | None`); no bcrypt (hashing lives in Wagner)
- `backend/app/core/logging.py` — Backend logging setup (wraps alphaforge-logger + Dante `redactor` scrubs every log record)
- `backend/app/core/deps.py` — `get_current_user` stateless JWT validation → `UserClaims(id, role, email)`; `require_owner`; optional Dante posture step-up
- `backend/app/modules/__init__.py` — registers every feature router under `/api/v1/*`
- `backend/app/modules/iam/iam_proxy.py` — thin httpx reverse proxy; forwards all `/api/v1/iam/*` to Wagner `:8001/iam/*`
- `frontend/src/modules/auth/auth.api.ts` — IAM client: fetches `GET /iam/login-key` once (cached), verifies the RSA-PSS mode signature, then sends `{encrypted_payload}` in prod or plain `{email, password}` in dev. Includes session management (`listSessions`, `extendSession`, `revokeSession`) and `logoutAll`.
- `frontend/src/modules/auth/auth.query.ts` — React Query hooks: `useSessions`, `useExtendSession`, `useRevokeSession`
- `frontend/src/modules/auth/auth.types.ts` — TypeScript mirrors of IAM schemas: `LoginKeyResponse`, `SessionResponse`, user/token types
- `frontend/src/modules/auth/useAuthStore.ts` — Zustand store; `logout()` revokes the current session then clears local state; `silentRefresh()` serializes concurrent 401 retries; persisted under `af-auth`
- `frontend/src/modules/preferences/SessionsGroup.tsx` — Sessions panel in Account preferences: lists active sessions with extend/revoke per row; "Sign out this device" triggers `logout()` + redirect
- `frontend/src/modules/preferences/PrivacySection.tsx` — "Sign out everywhere" calls `logoutAll()` + `clearAuth()` + redirect to `/login`
- `backend/app/modules/chat/` — Alpha chat module: `chat_routes.py` (`POST /api/v1/chat/` → SSE), `chat_service.py` (gateway dispatch + streaming), `chat_schemas.py` (request schema + model→QueryType mapping)
- `backend/app/modules/brokers/base.py` — `BrokerSource` ABC; implement for new brokers
- `backend/app/modules/brokers/registry.py` — broker source registry (slug → class)
- `backend/app/modules/brokers/dump_utils.py` — shared CSV-dump utilities (path, permissions, headers, P&L). See [broker-csv-dumps.md](broker-csv-dumps.md)
- `backend/app/modules/contracts/contracts_codegen.py` — Pydantic contract models → generated frontend TS (`just contracts-gen`); `tests/test_contracts_sync.py` is the drift guard. See [contracts.md](contracts.md)
- `backend/app/modules/marketdata/gate0_integrity.py` — `assert_no_leak()` rejects a universe with look-ahead / survivorship leakage; `bhavcopy_ingest.py` parses NSE bhavcopy (reusing `dump_utils` I/O) + builds the point-in-time `universe_as_of`. Probe: `just probe gate0`
- `backend/app/modules/funding/funding_subscriptions.py` — `opex_per_month()` from `subscriptions.toml` (INR via `brokers.fx`) — the self-funding denominator
- `backend/app/modules/edges/trial_ledger.py` — append-only, counts-only trial-budget ledger (overfitting integrity); `null_selftest.py` — `just null-data` random-data trust check (no edge in noise)
- `backend/app/modules/concierge/` — Orff concierge backend, wired to the **Fux brain** on both paths (the §18 vision: Fux serves Claude Code at dev-time and Orff at runtime):
  - `concierge_service.py` — `stream_chat` streams provider tokens as SSE. **Grounded in Fux**: before streaming it calls `fux_bridge.recall(last_user_msg)` (→ `fux hook-recall`) and injects the returned rules/glossary/memory bodies as an authoritative system message (`_GROUNDING_PREAMBLE`), so replies cite the project's real formulas (e.g. `day-pnl`, `portfolio-valuation`) instead of inventing them. Best-effort: grounding failure or an empty prompt simply skips injection — chat never breaks.
  - `fux_bridge.py` — subprocess bridge to the `fux` CLI (not import, so Orff talks to the same brain across venvs; $0, deterministic). `registry()` → `fux components`, `validate(spec)` → `fux validate-spec`, `recall(prompt)` → `fux hook-recall` (runtime grounding), `record_feedback(outcome)` → `fux feedback` (learning loop)
  - `prompt_service.py` — `assemble(req)` builds the message stack (system, Fux grounding, **elgar user-context memory**, holdings disclosure, history) and resolves routing (privacy floor → vision floor → pinned model), returning a `trace` of data-read steps the stream surfaces as collapsible tool events
  - `stream_events.py` — SSE framing helpers: `sse()`, secret `redact()`, and `split_thinking()` (peels a `<think>…</think>` reasoning trace off the visible answer for reasoning models)
  - `memory_service.py` — the user-editable context doc (`load_memory`/`save_memory`), **stored in the elgar store** (`elgar get/save orff-context`) not a home-dir file — financial prefs are money-adjacent (`plan-store` rule). Reached via `plans.elgar_bridge`
  - `history_service.py` — conversation history in its **own elgar collection** (`store/sessions/*.session.md`, separate from money `plans/`), one doc per chat: `save_session`/`load_session`/`list_sessions`/`delete_session`. The doc is a human-readable transcript plus a machine block for lossless resume; the store's git log is the conversation's audit trail. Best-effort, like memory. The collection is selected via the elgar `--dir` flag, threaded through `plans.elgar_bridge` (`save`/`get`/`list_docs`/`remove` all take `collection`). `render_session(updated=, source=)` is the deterministic, provenance-taggable renderer importers reuse
  - `claude_import.py` + `claude_parse.py` — re-runnable sync (`just sync-claude-history [--dry-run]`) that copies investment-related local Claude Code chats (`~/.claude/projects/*.jsonl`) into the `sessions/` collection. `claude_parse` strips tool calls/results and system/command wrappers to a clean You/Orff transcript; `claude_import` keyword-filters on the human's prompts and upserts under a stable `claude-<sessionId>` id (idempotent — deterministic render keyed on transcript mtime). Verified by `just probe claude-import`
  - `followup_service.py` — `suggest_followups()` generates 3 tap-to-send next-step chips via a cheap FACTOID completion; `action_service.py` — `detect_action()` returns a structured approval card for mutating intents (rebalance/buy/deploy/sync)
  - `compose_service.py` + `compose_prompt.py` + `compose_schemas.py` — on-the-fly UI generation: Orff emits a declarative UISpec (JSON tree, never code), validated server-side against the Fux component registry before the frontend renders it from a whitelist. Governed by the `ui-component-contract` rule
  - `concierge_routes.py` / `concierge_schemas.py` — SSE chat, `POST /concierge/compose`, `GET/PUT /concierge/memory`, and `GET /concierge/history` + `GET/PUT/DELETE /concierge/history/{id}` endpoints; `ChatMessage.images` carries vision attachments (data URLs, capped); `stt_service.py` — speech-to-text for the voice bar
  - **Stream event protocol** — `stream_chat` emits typed SSE events (token snapshot with `cost_usd`, `tool`, `thinking`, `confirm`, `spec`, `followups`, `error`+`[DONE]`); the full table lives in [concierge/README.md](../concierge/README.md). Verified by `just probe concierge-events`
### Frontend
- `frontend/src/app/layout.tsx` — Root layout. Mounts `ThemeProvider` → `QueryProvider` → `AuthGuard` → `BootGate` → `ChatProvider`, so the boot sequence and the global AlphaBar + ChatRail run once for the whole app across all routes
- `frontend/src/app/page.tsx` — Terminal landing page (no longer wraps `BootGate` — that's now in the root layout)
- `frontend/src/app/portfolio/page.tsx` — Portfolio page. Slim `PortfolioCompactBar` on top (TOTAL · INVESTED · P&L · DAY inline + wallet pills + a "More/Less" expand toggle) so tree / ledger get the dominant vertical space; expanded state reveals the full `WalletStrip`. Source spotlight + filter bar + summary + body (treemap or ledger) on the left, rebalance rail on the right. Filter state (query, sector chip, gainers/losers, sort key + dir, view, expand) is owned here
- `frontend/src/modules/portfolio/PortfolioCompactBar.tsx` — Hi-Fi `.pf-summary-bar`: always-visible row with totals + wallet pills + expand caret. Mirrors the design's "Less / More" pattern so a single click reveals stat cards beneath
- `frontend/src/modules/portfolio/WalletStrip.tsx` + `WalletCard.tsx` — Per-broker wallet cards with brand-colored chip, free cash, holdings value, position count, weighted day move. Shown when the CompactBar is expanded; clicking filters the page to that source. Strip has three action buttons: **⟳ Refresh cash** (`POST /portfolio/wallets/sync`), **⟳ Refresh holdings** (`POST /portfolio/sources/sync-all`), **⟳ Refresh** (hard refresh: busts all CSV caches then re-syncs sources + wallets via `POST /portfolio/refresh`)
- `frontend/src/modules/portfolio/SourceSpotlight.tsx` — Detail banner shown when a specific wallet is active (positions / holdings / P&L / cash). The `⟳ Refresh` button syncs both cash (`POST /portfolio/wallets/{slug}/sync`) and holdings (`POST /portfolio/sources/{slug}/sync`) in parallel, then invalidates wallets + holdings + treemap queries
- `frontend/src/modules/portfolio/FilterBar.tsx` (composes `SearchBox`, `SectorChips`, `PnLToggle`, `SortMenu`, `SegmentedControl` for the Tree/Ledger toggle) — Sector counts re-compute under search+pnl so the chips only show what's reachable; `/` and `⌘F` focus the search box
- `frontend/src/modules/portfolio/portfolio.filter.ts` — `FilterState`, `applyFilter`, `sectorCounts` helpers (pure functions, no React)
- `frontend/src/modules/portfolio/treemap.utils.ts` — Squarified-treemap layout in TS (mirrors `backend/app/modules/brokers/treemap_helper.py`); `Treemap.tsx` consumes filtered holdings + computes layout client-side so reflows are instant when filters change
- `frontend/src/app/preferences/page.tsx` — Preferences page. 8-section sidebar (Appearance · Display · Markets · Alpha AI · Notifications · Account · Privacy · About); reached via gear icon in the top-right
- `frontend/src/modules/preferences/` — Sidebar, section panels, and shared primitives:
  - `PrefRow` / `PrefGroup` / `PrefControls` (`PrefSeg`, `PrefTog`, `PrefSlider`, `PrefSelect`, `PrefInput`) — imported from `@alphaforge-anton/solar-ui`; no longer local files
  - `usePrefStore.ts` — Local-state hook for non-wired draft preferences. Persists to `localStorage["af-prefs-draft-v1"]`, mirrors `chromeMode`/`showVoice` to `body.chrome-autohide` / `body.no-voice` classes
  - `AppearanceSection.tsx` — Theme tiles + accent swatches (wired to `useTheme()`)
  - `DisplaySection.tsx` — Chrome behavior (always-visible vs auto-hide), voice bar toggle, orb size/speed/HUD, ticker speed, reduce motion, number jitter
  - `MarketsSection.tsx` — Primary exchange, number format, currency, after-hours, refresh cadence
  - `AlphaSection.tsx` — Voice wake, reply style, confidence floor, auto-rebalance, screener visibility
  - `NotifSection.tsx` — Price/risk/signal toggles, threshold slider, email digest cadence + address
  - `AccountSection.tsx` — Profile (avatar, name, status), connected brokers list, hotkey reference
  - `PrivacySection.tsx` — Telemetry / crash / training toggles, retention select, danger actions
  - `AboutSection.tsx` — Build / backend / license info, reset action
- `frontend/src/app/globals.css` — Theme variables (Solar Terminal design tokens); `@source` directives extend Tailwind v4 content scanning into `packages/solar-ui/src` so arbitrary classes in solar-ui resolve; restores the default `cursor: pointer` on `button` / `[role="button"]` that Tailwind v4's Preflight dropped
- `frontend/next.config.mjs` — Next.js config: CSP headers (allows `fonts.googleapis.com` + `fonts.gstatic.com` for Material Symbols icons), API rewrites
- `frontend/src/modules/dashboard/TerminalTopBar.tsx` — Slim global top bar per Hi-Fi spec (≈32px min-height, 4px×14px padding, 8px radius). SVG logo mark + ALPHA/FORGE wordmark; Terminal + Portfolio nav buttons; gear icon-button on the right routes to `/preferences`; no icon sidebar
- `frontend/src/modules/concierge/` — Alpha concierge module (Command Console design):
  - `AlphaBar.tsx` — Global bottom footer bar (4 states): **Voice** (8-bar waveform + rotating prompt + model picker), **Chat command-line** (single-line textarea `#chatinput-bar` + model picker), **ComposeCard** (multiline card with model picker, grows on scroll), **CollapsedStrip** (live-dot + ESC when rail open). The model label in every state is the clickable `ModelPicker` dropdown (not static text) — click it to switch model in-place. Mode-seg (Voice/Chat tabs) container is 26px with `align-items:stretch`. Clicking Chat shows the footer textarea; the rail opens after the user submits a message, **or immediately on double-clicking the Voice/Chat toggle** (`onDoubleClick` → forces chat mode + `onChatModeOpen`). Uses `useVoice` hook directly.
  - `ChatRail.tsx` — Center-positioned slide-over conversation panel. Layout: left nav sidebar (58px — Chat / Artifacts / Memory / voice-readback / ⌘K) + main content column that swaps the thread for the Artifacts or Memory panel. Header carries the `SessionMeter` (live token + USD cost) and a Stop control while streaming. Composer adds a `/`-triggered `CommandMenu`, image attach + paste, and a Stop button. `TurnPair` renders the data-read `ToolTrail`, `ThinkingBlock`, `ApprovalCard`, and `FollowupChips`, plus an edit-and-branch affordance and image thumbnails. `ResponseBody` renders markdown as safe React nodes (no `dangerouslySetInnerHTML`).
  - Feature components: `ArtifactsPanel` / `MemoryPanel` / `HistoryPanel` (side panels; history lists/resumes/deletes elgar-backed sessions via `concierge.history.ts` + `concierge.sessions.ts` auto-save) · `ToolTrail` / `ThinkingBlock` / `Disclosure` (collapsible process blocks) · `ApprovalCard` (action confirmations) · `FollowupChips` · `SessionMeter` · `ImageAttach` (vision) · `CommandMenu` + `CommandPalette` (⌘K) over `concierge.commands.ts` · `chat.export.ts` (Markdown download) · `chat.images.ts` (paste/file → data URL)
  - `ModelPicker.tsx` — Model dropdown: Auto / Forge Pro / Forge Fast / Forge Local
  - `useChatStream.ts` — SSE fetch hook: multi-turn history up to 6 turns, `submit(q, choice, images)`, `editTurn` (branch), `stop` (abort mid-stream), and session `totals`; forwards JWT from `localStorage["af_token"]`. `chat.events.ts` holds the typed `StreamPayload` + `reduceEvent` reducer (one branch per event kind, additive)
  - `concierge.memory.ts` — `useConciergeMemory` / `useSaveMemory` react-query hooks over `GET/PUT /concierge/memory`
  - `ChatContext.tsx` — React context provider rendering AlphaBar + ChatRail globally; manages `ModelChoice` state, persisted to `localStorage["af-model-choice"]`
  - `concierge.types.ts` — `ChatTurn` (now with `thinking`/`tools`/`confirm`/`followups`/`costUsd`/`images`), `ToolStep`, `PendingAction`, `activeModelFor`, `formatChoiceLabel`
  - Mounted in `layout.tsx` as `<ChatProvider>` so it appears on every screen. **Security:** backend endpoint is JWT-gated (`Depends(get_current_user)`); frontend proxy (`/api/v1/concierge` → `route.ts`) keeps provider API keys server-side only.
- `frontend/src/modules/dashboard/TerminalVoice.tsx` — Legacy static voice dock (no longer rendered — replaced by `AlphaBar` from the chat module)
- `packages/solar-ui/src/components/TopBar.tsx` / `VoiceDock.tsx` — Reusable chrome containers carrying `data-af-top` / `data-af-voice` plus `.af-top` / `.af-voice` classes. Paired with `body.chrome-autohide` / `body.no-voice` rules in `frontend/src/app/globals.css` to enable Preferences → Display → Chrome behavior (collapses bars to an accent strip; hover/focus expands) and the voice-bar disable toggle
- `frontend/src/modules/dashboard/BootScreen.tsx` — Full-screen animated boot checklist. Renders one row per real backend system (gateway, Postgres, every broker source); each row's glyph and detail are driven by the `status: BootStatus` field (`ok` ✓ green / `warn` ! amber / `error` ✗ red). `BOOT_STEPS` is the static fallback used only when the live probe fails
- `frontend/src/modules/dashboard/boot.api.ts` + `boot.types.ts` — Frontend client and TS mirror of `BootReport` / `BootService` from the backend
- `frontend/src/modules/dashboard/BootGate.tsx` — Sits inside `AuthGuard` in the root layout. On first paint of a tab it hits `GET /api/v1/health/boot`, maps each service to a `BootStep`, then plays the boot screen exactly once per browser tab (gated by `sessionStorage['af-booted']`). Skips entirely on `/login` and survives navigations between Terminal / Portfolio / Preferences. If the probe call fails the static `BOOT_STEPS` fallback still produces a usable splash
- `backend/app/modules/health/health_routes.py` — `GET /health` (basic ping) + `GET /health/boot` (per-system readiness snapshot consumed by the terminal boot splash; aggregates database SELECT 1 + every broker source's `.status` from `SOURCES`)
- `backend/app/modules/health/boot_probes.py` — One probe function per system (`probe_backend`, `probe_database`, `probe_brokers`). Each probe swallows its own errors so a single failure can't take down the whole `/health/boot` response
- `backend/app/modules/health/boot_schemas.py` — `BootStatus` enum (`ok` / `warn` / `error` / `skip`), `BootService`, and `BootReport` Pydantic v2 schemas; the frontend mirror is `boot.types.ts`
- `frontend/src/modules/dashboard/TerminalRail.tsx` — Icon sidebar (unused; nav lives in the top bar per Hi-Fi design)
- `frontend/src/lib/api.ts` — Axios HTTP client (interceptors only; per-domain `*.api.ts` lives in each module). The response interceptor handles 401 → silent refresh → redirect and attaches a normalized `ApiError` as `error.apiError` on every failed request.
- `frontend/src/lib/apiError.ts` — `ApiError` type + `toApiError()` normalizer. All HTTP errors collapse to a typed shape with `kind` (`network/canceled/auth/forbidden/notFound/validation/client/server/unknown`), `status`, `message`, and optional `detail`/`requestId`.
- `frontend/src/lib/apiNotify.ts` — `notifyApiError(err)`: bridges an `ApiError` to a `notify.error()` toast. Skips `canceled` (unmount noise) and `auth` (interceptor already handles redirect).
- `frontend/src/lib/providers.tsx` — React Query `QueryProvider`. Global error handlers: mutations always call `notifyApiError` (suppress with `meta: { silent: true }`); queries are silent unless `meta: { notifyOnError: true }`. See [conventions.md § Error Handling](conventions.md#error-handling--notifications).
- `frontend/src/lib/logger.ts` — Frontend logging setup (wraps @alphaforge/logger)
- `frontend/src/modules/<name>/<name>.api.ts` — Per-domain axios calls
- `frontend/src/modules/<name>/<name>.query.ts` — Per-domain React Query hooks

### Packages & Infra
- `packages/logger-py/src/alphaforge_logger/logger.py` — Python logger package core
- `packages/logger-node/src/logger.ts` — Node/TS logger package core
- `packages/solar-ui/src/index.ts` — UI library barrel export (Button, Input, Card, Badge, Icon, Text, SearchBox, PrefRow, PrefGroup, PrefControls, …)
- `packages/solar-ui/src/styles/theme.css` — Tailwind v4 design tokens (CSS)
- `packages/solar-ui/src/tokens/index.ts` — Design tokens (TypeScript)
- `packages/solar-ui/src/tokens/tokens.json` — Design tokens (JSON, machine-readable)
- `packages/solar-ui/tsup.config.ts` — Package build config
- `repo-context-mcp/src/alphaforge_anton_repo_context/server.py` — MCP server entry (stdio); exposes `search_code`, `get_symbol`, `module_overview`, `recent_changes`, `read_file_range`
- `repo-context-mcp/src/alphaforge_anton_repo_context/indexer.py` — Walk → chunk → embed → pgvector
- `repo-context-mcp/src/alphaforge_anton_repo_context/chunker.py` — AST (Python), regex (TS/TSX), section (Markdown), sliding-window fallback
- `repo-context-mcp/src/alphaforge_anton_repo_context/db.py` — `repo_chunks` ORM model + `init_schema()`
- `repo-context-mcp/README.md` — Wire-up snippets for Claude Code, VS Code/Copilot, Cursor, Cline, Zed, Windsurf

### Probes & Design
- `probes/ui_probe.py` — End-to-end UI smoke test via CDP (port 9299). Attaches to existing Chrome session; exercises auth, dashboard, portfolio, and console-error checks. Writes PNGs to `/tmp/alphaforge-anton-probe/`
- `probes/ui_screens.py` — Lightweight screenshot helper. Auths via `POST /api/v1/auth/token`, stashes the JWT in localStorage, then snapshots `/`, `/portfolio`, `/preferences` at 1440×900
- `probes/ui_pref_tabs.py` — Walks every Preferences sidebar tab and captures `preferences-<tab>.png` for design review
- `screenshots/` — Probe output. Tracked dir; PNGs are overwritten on each run
- `design/` — Bundle from Claude Design (`design/README.md`, `design/chats/` transcripts, `design/project/Alpha Forge Hi-Fi.html` + companion JSX prototypes). Source of truth for visual / interaction specs

### Config & Workspace
- `.python-version` — Python version for pyenv (3.14.2)
- `.nvmrc` — Node.js version for nvm
- `.npmrc` — pnpm/npm configuration (exact versions, engine-strict)
- `pyproject.toml` (repo root) — uv workspace definition + `[tool.uv.sources]` for local deps
- `uv.lock` (repo root) — single lockfile for all Python workspace members
- `pnpm-workspace.yaml` — Workspace root definition
- `.env.port` — All service ports in one file (single source of truth for BACKEND_PORT, FRONTEND_PORT, POSTGRES_PORT, REDIS_PORT)
- `.env` — App config defaults + LLM key stubs (tracked; no secrets)
- `.env.cred.example` — Credentials template (AFBACH, BROKER_CACHE_KEY, JWT, POSTGRES_PASSWORD)
- `.env.frontend.example` — Frontend env template (NEXT_PUBLIC_API_URL, ports, logging)
- `.env.cred.local` / `.env.frontend.local` — Real secrets/overrides (gitignored; created by `./setup-config.sh`)
- `frontend/.env.local` — Symlink → `../.env.frontend.local`; Next.js auto-loads it from its project root
- `.vscode/mcp.json` — VS Code MCP server config
