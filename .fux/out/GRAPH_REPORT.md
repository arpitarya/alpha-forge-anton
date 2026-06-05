# Fux GRAPH_REPORT

_1387 nodes · 6936 edges · 341 code files · 24 rules · 161 communities._

## Node types

- function: 931
- code-file: 341
- class: 91
- narrative: 11
- convention: 4
- memory: 3
- regulatory: 2
- formula: 2
- invariant: 1
- rule: 1

## God nodes (highest connectivity)

- **get** (function) — 153 edges
- **angelone_dump.py** (code-file) — 76 edges
- **binance_dump.py** (code-file) — 76 edges
- **groww_dump.py** (code-file) — 76 edges
- **indmoney_dump.py** (code-file) — 76 edges
- **tickertape_dump.py** (code-file) — 76 edges
- **zerodha_coin_dump.py** (code-file) — 76 edges
- **zerodha_kite_dump.py** (code-file) — 76 edges
- **cerebras.py** (code-file) — 75 edges
- **groq.py** (code-file) — 75 edges
- **mistral.py** (code-file) — 75 edges
- **openrouter.py** (code-file) — 75 edges

## Chokepoints (PageRank centrality)

- **get** (function) — 0.0118
- **ChatRail.tsx** (code-file) — 0.0046
- **info** (function) — 0.0039
- **test_brokers.py** (code-file) — 0.0039
- **auth.api.ts** (code-file) — 0.0036
- **post** (function) — 0.0032
- **portfolio.query.ts** (code-file) — 0.0031
- **openrouter.py** (code-file) — 0.0029
- **cerebras.py** (code-file) — 0.0029
- **groq.py** (code-file) — 0.0029
- **mistral.py** (code-file) — 0.0029
- **huggingface.py** (code-file) — 0.0028

## Communities

- **community 0** (823 nodes): AccountSection, AllocationSlice, AlphaSection, AlphaSection.tsx, AngelOneSource, AppearanceSection, AppearanceSection.tsx, AssetClass, BinanceSource, BootReport, BootScreen, BootScreen.tsx
- **community 1** (15 nodes): 1d8f1014a7d4_dashboard_ticker_watchlist_items.py, 640eee61bc50_initial_schema_with_pgvector_memory.py, Text, Text.tsx, _table, a3c9f2e1b4d7_iam_tables.py, b3d6f8a2c9e1_remove_iam_tables.py, downgrade, downgrade, downgrade, downgrade, upgrade
- **community 4** (16 nodes): Base, Base, RepoChunk, Settings, Settings, _find_repo_root, _validate_secrets, config.py, config.py, database.py, db.py, get_db
- **community 5** (7 nodes): UserClaims, decode_access_token, deps.py, get_current_user, require_owner, security.py, user_from_jwt
- **community 6** (5 nodes): Order, _repo_root, env_loader.py, get_env_files, load_env_files
- **community 12** (12 nodes): _fetch_live_usd_inr, _load_cached, _path, _path, _read_all, _read_all, _write_all, _write_row, cash_dump.py, fx.py, get_inr_per_usd, save_cash
- **community 16** (11 nodes): Treemap, Treemap.tsx, _worst, aspectRatio, itemShort, squarify, squarify, stripLen, treemap.utils.ts, treemap_helper.py, worstAspect
- **community 20** (3 nodes): ChatMessage, ChatRequest, concierge_schemas.py
- **community 22** (18 nodes): DashboardTickerItem, DashboardWatchlistItem, _now, _seed_ticker, _seed_watchlist, add, add_ticker, add_watchlist, dashboard_models.py, dashboard_repo.py, delete_ticker, delete_ticker
- **community 23** (21 nodes): BriefBlock, CreateTickerItemRequest, CreateWatchlistItemRequest, DashboardStats, RiskMeter, StatCard, TerminalBrief, TickerItem, WatchlistItem, _fmt_inr_short, _ticker_dto, _watchlist_dto
- **community 38** (36 nodes): ChatProvider, ChatRail, ChatRail.tsx, CrBtn, EmptyState, InlineTokens, Kbd, Kbd, Kbd.tsx, ModelPicker, ModelPicker.tsx, OrbAvatar
- **community 40** (21 nodes): FilterBar, FilterBar.tsx, PortfolioHeader, PortfolioHeader.tsx, applyFilter, assetClassCounts, bucketOf, equitySubOf, ex, isInvitReit, isUSEquity, matchQuery
- **community 42** (11 nodes): QueryProvider, apiError.ts, apiNotify.ts, d, extractDetail, isApiError, kindFromStatus, notifyApiError, providers.tsx, shouldRetry, toApiError
- **community 45** (13 nodes): _importPublicKey, _pemToBytes, auth.api.ts, createApiKey, deleteApiKey, encryptCredentials, getLoginKey, invalidateLoginKey, listApiKeys, listSessions, loginUser, registerUser
- **community 46** (2 nodes): AuthGuard, auth.guard.tsx
- **community 48** (8 nodes): AlphaBar, AlphaBar.tsx, ChatIcon, DeployButton, MicIcon, ModeBtn, ModeSegment, handleModeChange
- **community 49** (3 nodes): ChatContext.tsx, loadChoice, useChat
- **community 50** (6 nodes): ActiveDot, AutoRow, ModelPicker.rows.tsx, ModelRow, ProvRow, Tag
- **community 52** (5 nodes): MicToggle, VoiceCenter.tsx, Waveform, Waveform, Waveform.tsx
- **community 55** (3 nodes): err, start.sh, stop.sh
- **community 56** (2 nodes): getSRCtor, webspeech.types.ts
- **community 57** (3 nodes): AlphaBriefCard, AlphaBriefCard.tsx, useDashboardBrief
- **community 58** (16 nodes): BlockingBoot, BootGate, BootGate.tsx, announce, blockers, diagnose, emitProgress, fetchBootReport, isBlocking, isBrokerRow, isCached, reloadAction
- **community 59** (2 nodes): MarketOverview, MarketOverview.tsx
- **community 60** (2 nodes): OrbStage, OrbStage.tsx
- **community 61** (11 nodes): ActionBtn, SessionsGroup.tsx, SignOutBtn, TerminalRail, TerminalRail.tsx, TerminalTopBar, TerminalTopBar.tsx, handleLogout, handleLogout, isActive, isActive
- **community 62** (3 nodes): TerminalStats, TerminalStats.tsx, useDashboardStats
- **community 63** (5 nodes): TerminalTicker, TerminalTicker.tsx, useAddTickerItem, useDashboardTicker, useDeleteTickerItem
- **community 64** (2 nodes): TerminalVoice, TerminalVoice.tsx
- **community 65** (6 nodes): WatchlistCard, dashboard.query.ts, useAddWatchlistItem, useDashboardRisk, useDashboardWatchlist, useDeleteWatchlistItem
- **community 66** (5 nodes): boot.diagnose.ts, copyAndConfirm, plural, slugList, truncate
- **community 70** (3 nodes): AssetClassFilter, AssetClassFilter.tsx, ChipGroup
- **community 71** (2 nodes): Ledger, Ledger.tsx
- **community 72** (26 nodes): LedgerRow, LedgerRow.tsx, PortfolioCompactBar, PortfolioCompactBar.tsx, SourceSpotlight, SourceSpotlight.tsx, SpotStat, SummaryBar, SummaryBar.tsx, WalletCard, WalletCard.tsx, WalletPill
- **community 73** (2 nodes): PnLToggle, PnLToggle.tsx
- **community 74** (3 nodes): RebalanceRail, RebalanceRail.tsx, useRebalance
- **community 75** (3 nodes): SourceActions, SourceActions.tsx, showSync
- **community 76** (2 nodes): SourceOtpDialog, SourceOtpDialog.tsx
- **community 77** (6 nodes): SourceRow, SourceRow.tsx, detail, formatTime, sources.utils.ts, statusVariant
- **community 78** (23 nodes): SourcesPanel, SourcesPanel.tsx, handleReset, handleStartLogin, handleSubmitOtp, handleSync, handleSyncAll, onAfter, portfolio.query.ts, r, readErr, useForceRefresh
- **community 79** (6 nodes): StripButton, WalletStrip, WalletStrip.tsx, handleForceRefresh, handleRefreshHoldings, handleSyncCash
- **community 82** (3 nodes): AboutSection, AboutSection.tsx, StaticBox
- **community 83** (3 nodes): AccountSection.tsx, Hotkey, initial
- **community 84** (8 nodes): PreferencesScreen.tsx, PreferencesSidebar, PreferencesSidebar.tsx, isDeepEqual, modifiedCount, notifications.types.ts, tag, tag
- **community 85** (2 nodes): SectionIcon, SectionIcon.tsx
- **community 86** (2 nodes): StubSection, StubSection.tsx
- **community 89** (2 nodes): ScreenerPanel, ScreenerPanel.tsx
- **community 92** (9 nodes): Chunk, _chunk_markdown, _chunk_python, _chunk_ts_like, _chunk_window, chunk_file, chunker.py, content_hash, detect_lang
- **community 98** (2 nodes): Playground, Playground.tsx
- **community 100** (3 nodes): SolarOrb, SolarOrb.tsx, hexToGlow
- **community 104** (2 nodes): AppShell, AppShell.tsx
- **community 105** (2 nodes): Badge, Badge.tsx
- **community 106** (2 nodes): BootStep, BootStep.tsx
- **community 108** (3 nodes): Card, Card.tsx, CardHeader
- **community 109** (2 nodes): Chip, Chip.tsx
- **community 110** (4 nodes): CountUp, CountUp.tsx, formatNumber, step
- **community 111** (2 nodes): Divider, Divider.tsx
- **community 112** (2 nodes): HudCorners, HudCorners.tsx
- **community 113** (2 nodes): Icon, Icon.tsx
- **community 114** (2 nodes): IconRail, IconRail.tsx
- **community 116** (3 nodes): LiveDot, LiveDot.tsx, dot
- **community 117** (3 nodes): AntonMark, Logo, Logo.tsx
- **community 118** (2 nodes): MicIndicator, MicIndicator.tsx
- **community 119** (7 nodes): PrefControls.tsx, PrefInput, PrefSeg, PrefSelect, PrefSlider, PrefTog, v
- **community 120** (2 nodes): PrefGroup, PrefGroup.tsx
- **community 121** (2 nodes): PrefRow, PrefRow.tsx
- **community 122** (2 nodes): ProgressBar, ProgressBar.tsx
- **community 123** (2 nodes): RiskBars, RiskBars.tsx
- **community 124** (3 nodes): SearchBox, SearchBox.tsx, handle
- **community 125** (2 nodes): SegmentedControl, SegmentedControl.tsx
- **community 126** (2 nodes): Sparkline, Sparkline.tsx
- **community 127** (2 nodes): Stat, Stat.tsx
- **community 128** (2 nodes): Swatches, Swatches.tsx
- **community 129** (4 nodes): ThemeProvider, ThemeProvider.tsx, readPersisted, writePersisted
- **community 130** (2 nodes): TopBar, TopBar.tsx
- **community 131** (2 nodes): VoiceDock, VoiceDock.tsx
- **community 132** (2 nodes): WatchRow, WatchRow.tsx
- **community 133** (10 nodes): Notification, Notification.tsx, beginExit, cancelTtl, dismissNotification, fmtDateTime, fmtTime, notify.ts, severityIcon, startTtl
- **community 134** (2 nodes): NotificationsHost, NotificationsHost.tsx
- **community 136** (7 nodes): CloseIcon, Err, Info, Ok, Sync, Warn, notifications.icons.tsx
- **community 137** (9 nodes): clearNotifications, defaultTtl, emit, getServerSnapshot, getSnapshot, nextId, notifications.store.ts, pushNotification, useNotifications
- **community 143** (6 nodes): anton-overview, day-pnl, holdings-sum-equals-total, inr-normalization, portfolio-valuation, project-wagner-dante
- **community 150** (2 nodes): doc-per-code-change, files-max-100-lines
