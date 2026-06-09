# Fux GRAPH_REPORT

_1538 nodes · 7137 edges · 349 code files · 25 rules · 197 communities._

## Node types

- function: 924
- code-file: 349
- class: 240
- narrative: 11
- convention: 5
- memory: 3
- regulatory: 2
- formula: 2
- invariant: 1
- rule: 1

## Edges

_4028 of 7137 are INFERRED (low-confidence `references`, down-weighted in clustering/centrality)._

- references: 4028
- calls: 1921
- contains: 1166
- related: 14
- governs: 8

## God nodes (highest connectivity)

- **get** (function) — 159 edges
- **run** (function) — 78 edges
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

## Chokepoints (PageRank centrality)

- **get** (function) — 0.0142
- **ChatRail.tsx** (code-file) — 0.0045
- **info** (function) — 0.0044
- **post** (function) — 0.0043
- **portfolio.types.ts** (code-file) — 0.0038
- **PrefControls.tsx** (code-file) — 0.0038
- **test_brokers.py** (code-file) — 0.0037
- **fetch** (function) — 0.0033
- **fetch** (function) — 0.0032
- **portfolio.query.ts** (code-file) — 0.0031
- **auth.types.ts** (code-file) — 0.0028
- **AlphaBar.tsx** (code-file) — 0.0028

## Communities

- **community 0** (4 nodes): do_run_migrations, env.py, run_migrations_offline, run_migrations_online
- **community 1** (4 nodes): 1d8f1014a7d4_dashboard_ticker_watchlist_items.py, _table, downgrade, upgrade
- **community 2** (12 nodes): 640eee61bc50_initial_schema_with_pgvector_memory.py, Text, Text.tsx, TextProps, a3c9f2e1b4d7_iam_tables.py, b3d6f8a2c9e1_remove_iam_tables.py, downgrade, downgrade, downgrade, upgrade, upgrade, upgrade
- **community 5** (3 nodes): Settings, _validate_secrets, config.py
- **community 6** (3 nodes): Base, database.py, get_db
- **community 7** (7 nodes): UserClaims, decode_access_token, deps.py, get_current_user, require_owner, security.py, user_from_jwt
- **community 8** (4 nodes): _repo_root, env_loader.py, get_env_files, load_env_files
- **community 10** (10 nodes): create_app, lifespan, logger.py, logging.py, main.py, setup_logging, setup_logging, test_log_writes_to_file, test_logger.py, test_setup_logging_creates_dir
- **community 11** (695 nodes): AngelOneSource, AssetClass, Base, BinanceSource, BraveSource, BrokerSource, BseAnnouncementsSource, CerebrasAdapter, ClaudeSdkAdapter, CompleteIn, ComposeRequest, ComposeResponse
- **community 14** (6 nodes): _cache_root, _check_dev_host, _fernet, _http.py, load_session, save_session
- **community 15** (31 nodes): AllocationSlice, HoldingsAggregator, RebalanceDrift, RebalanceSuggestion, TreemapCell, TreemapCell, TreemapCell.tsx, TreemapCellProps, _inr_invested, _inr_value, aggregator.py, aggregator_types.py
- **community 17** (38 nodes): AccountSection, AlphaSection, AlphaSection.tsx, AlphaSectionProps, AppearanceSection, AppearanceSection.tsx, AppearanceSectionProps, DisplaySection, DisplaySection.tsx, DisplaySectionProps, MarketsSection, MarketsSection.tsx
- **community 18** (12 nodes): _is_due, _prime_one, _prime_unsynced, _refetch_loop, _sync_one, _sync_one, boot_sync_stream, generate, health_routes.py, refetch.py, start_refetch_loop, sync
- **community 20** (4 nodes): _as_cash, cash_routes.py, get_cash, sync_one_cash
- **community 21** (7 nodes): _fetch_live_usd_inr, _load_cached, _path, _read_all, _write_row, fx.py, get_inr_per_usd
- **community 24** (2 nodes): _to_float, normalize
- **community 26** (5 nodes): Treemap, Treemap.tsx, _worst, squarify, treemap_helper.py
- **community 27** (5 nodes): WalletInfo, _aggregate_holdings, _build_one, list_wallets, wallet_aggregator.py
- **community 31** (3 nodes): _vocab, build_system, compose_prompt.py
- **community 32** (3 nodes): ChatMessage, ChatRequest, concierge_schemas.py
- **community 33** (6 nodes): _bin, _run, fux_bridge.py, record_feedback, registry, validate
- **community 35** (16 nodes): DashboardTickerItem, DashboardWatchlistItem, _now, _seed_ticker, _seed_watchlist, add, add_ticker, add_watchlist, dashboard_models.py, dashboard_repo.py, delete_ticker, delete_watchlist
- **community 36** (24 nodes): BriefBlock, CreateTickerItemRequest, CreateWatchlistItemRequest, DashboardStats, RiskMeter, StatCard, TerminalBrief, TickerItem, TickerItem, WatchlistItem, _fmt_inr_short, _ticker_dto
- **community 39** (15 nodes): BootReport, BootReport, BootService, BootService, BootStatus, SyncResult, _broker_detail, boot.types.ts, boot_probes.py, boot_report, boot_schemas.py, probe_backend
- **community 41** (3 nodes): _forward, iam_proxy, iam_proxy.py
- **community 44** (3 nodes): Order, Watchlist, portfolio_models.py
- **community 46** (2 nodes): _make_holding, _seed_zerodha
- **community 54** (2 nodes): RootLayout, layout.tsx
- **community 55** (7 nodes): ChatProvider, LoginPage, WatchlistCard.tsx, getMe, handleSubmit, page.tsx, submit
- **community 56** (2 nodes): Home, page.tsx
- **community 57** (23 nodes): AssetClassCounts, FilterBar, FilterBar.tsx, FilterBarProps, FilterState, PortfolioHeader, PortfolioHeader.tsx, PortfolioPage, applyFilter, assetClassCounts, bucketOf, equitySubOf
- **community 58** (2 nodes): PreferencesPage, page.tsx
- **community 59** (2 nodes): AxiosRequestConfig, api.ts
- **community 60** (12 nodes): ApiError, QueryProvider, Register, apiError.ts, apiNotify.ts, extractDetail, isApiError, kindFromStatus, notifyApiError, providers.tsx, shouldRetry, toApiError
- **community 61** (2 nodes): AppState, store.ts
- **community 63** (9 nodes): _importPublicKey, _pemToBytes, auth.api.ts, deleteApiKey, encryptCredentials, getLoginKey, invalidateLoginKey, loginUser, verifyModeSignature
- **community 64** (18 nodes): ActionBtn, DangerButton, PrivacySection, PrivacySection.tsx, PrivacySectionProps, SessionsGroup, SessionsGroup.tsx, SignOutBtn, auth.query.ts, device, fmt, handleLogout
- **community 65** (2 nodes): AuthGuard, auth.guard.tsx
- **community 66** (9 nodes): ApiKey, ApiKeyCreateRequest, IamUser, LoginKeyResponse, LoginRequest, RegisterRequest, SessionResponse, TokenResponse, auth.types.ts
- **community 67** (7 nodes): AuthState, applyHeader, errorMessage, errorStatus, requestPath, skipRefreshRetry, useAuthStore.ts
- **community 68** (9 nodes): AlphaBar, AlphaBar.tsx, ChatIcon, DeployButton, MicIcon, ModeBtn, ModeSegment, Props, handleModeChange
- **community 69** (4 nodes): ChatContext.tsx, ChatCtx, loadChoice, useChat
- **community 70** (19 nodes): ChatRail, ChatRail.tsx, CrBtn, EmptyState, InlineTokens, Kbd, OrbAvatar, Props, ResponseBody, SeedCard, SendButton, TurnPair
- **community 71** (3 nodes): DynamicRenderer, DynamicRenderer.tsx, Props
- **community 72** (9 nodes): ActiveDot, AutoRow, AutoRowProps, ModelPicker.rows.tsx, ModelRow, ModelRowProps, ProvRow, ProvRowProps, Tag
- **community 74** (14 nodes): ActiveModel, ChatTurn, ModelPicker, ModelPicker.tsx, Props, Resolved, activeModelFor, concierge.routing.ts, concierge.types.ts, lookup, onKey, onMouseDown
- **community 75** (4 nodes): MicToggle, Props, VoiceCenter.tsx, Waveform
- **community 76** (3 nodes): async-everywhere, compose.registry.ts, ui-component-contract
- **community 77** (3 nodes): ModelMeta, ProviderMeta, concierge.providers.ts
- **community 79** (7 nodes): SRErrorEvent, SREvent, SRResult, SRResultList, WebkitSR, getSRCtor, webspeech.types.ts
- **community 80** (3 nodes): AlphaBriefCard, AlphaBriefCard.tsx, useDashboardBrief
- **community 81** (17 nodes): BlockingBoot, BootGate, BootGate.tsx, announce, diagnose, emitProgress, fetchBootReport, isBlocking, isBrokerRow, isCached, reloadAction, runSync
- **community 82** (4 nodes): BootScreen, BootScreen.tsx, BootScreenProps, BootStep
- **community 83** (2 nodes): MarketOverview, MarketOverview.tsx
- **community 84** (2 nodes): OrbStage, OrbStage.tsx
- **community 85** (3 nodes): TerminalRail, TerminalRail.tsx, isActive
- **community 86** (3 nodes): TerminalStats, TerminalStats.tsx, useDashboardStats
- **community 87** (5 nodes): TerminalTicker, TerminalTicker.tsx, useAddTickerItem, useDashboardTicker, useDeleteTickerItem
- **community 88** (4 nodes): TerminalTopBar, TerminalTopBar.tsx, handleLogout, isActive
- **community 89** (2 nodes): TerminalVoice, TerminalVoice.tsx
- **community 90** (2 nodes): Watchlist, Watchlist.tsx
- **community 91** (6 nodes): WatchlistCard, dashboard.query.ts, useAddWatchlistItem, useDashboardRisk, useDashboardWatchlist, useDeleteWatchlistItem
- **community 92** (6 nodes): Diagnosis, Failure, Pattern, boot.diagnose.ts, copyAndConfirm, plural
- **community 93** (8 nodes): BriefBlockDTO, DashboardStatsDTO, RiskMeterDTO, StatCardDTO, TerminalBriefDTO, TickerItemDTO, WatchlistItemDTO, dashboard.types.ts
- **community 95** (5 nodes): AssetClassFilter, AssetClassFilter.tsx, AssetClassFilterProps, ChipGroup, ChipGroupProps
- **community 96** (4 nodes): ColDef, Ledger, Ledger.tsx, LedgerProps
- **community 97** (27 nodes): LedgerRow, LedgerRow.tsx, PortfolioCompactBar, PortfolioCompactBar.tsx, PortfolioCompactBarProps, SourceSpotlight, SummaryBar, SummaryBar.tsx, SummaryBarProps, WalletCard, WalletCard.tsx, WalletCardProps
- **community 98** (2 nodes): PnLToggle, PnLToggle.tsx
- **community 99** (4 nodes): RebalanceRail, RebalanceRail.tsx, RebalanceRailProps, useRebalance
- **community 100** (5 nodes): SortMenu, SortMenu.tsx, SortMenuProps, h, pick
- **community 101** (3 nodes): Props, SourceActions, SourceActions.tsx
- **community 102** (3 nodes): Props, SourceOtpDialog, SourceOtpDialog.tsx
- **community 103** (5 nodes): SourceRow, SourceRow.tsx, formatTime, sources.utils.ts, statusVariant
- **community 104** (4 nodes): SourceSpotlight.tsx, SourceSpotlightProps, SpotStat, onRefresh
- **community 105** (12 nodes): SourcesPanel, SourcesPanel.tsx, handleReset, handleStartLogin, handleSubmitOtp, handleSync, handleSyncAll, onAfter, readErr, useSourceRow.hook.ts, useSources, useSyncAll
- **community 106** (10 nodes): StripButton, WalletStrip, WalletStrip.tsx, WalletStripProps, handleForceRefresh, handleRefreshHoldings, handleSyncCash, useForceRefresh, useSyncAllSources, useSyncAllWallets
- **community 108** (8 nodes): FxResponseDTO, portfolio.query.ts, useResetSource, useSourceRow, useStartLogin, useSubmitOtp, useSyncSource, useTreemap
- **community 109** (12 nodes): AllocationSliceDTO, HoldingDTO, HoldingsResponseDTO, PortfolioTotalsDTO, RebalanceResponseDTO, SourceInfoDTO, SyncAllResultDTO, TreemapCellDTO, TreemapResponseDTO, WalletInfoDTO, WalletsResponseDTO, portfolio.types.ts
- **community 110** (5 nodes): Rect, aspectRatio, squarify, treemap.utils.ts, worstAspect
- **community 111** (4 nodes): AboutSection, AboutSection.tsx, AboutSectionProps, StaticBox
- **community 112** (3 nodes): AccountSection.tsx, AccountSectionProps, Hotkey
- **community 113** (7 nodes): PreferencesScreen.tsx, PreferencesSidebar, PreferencesSidebar.tsx, PreferencesSidebarProps, isDeepEqual, modifiedCount, onKey
- **community 114** (2 nodes): SectionIcon, SectionIcon.tsx
- **community 115** (3 nodes): StubSection, StubSection.tsx, StubSectionProps
- **community 117** (2 nodes): PrefSectionMeta, preferences.types.ts
- **community 118** (2 nodes): ScreenerPanel, ScreenerPanel.tsx
- **community 121** (9 nodes): Chunk, _chunk_markdown, _chunk_python, _chunk_ts_like, _chunk_window, chunk_file, chunker.py, content_hash, detect_lang
- **community 123** (3 nodes): _row_dict, get_symbol, get_symbol.py
- **community 124** (3 nodes): _walk_up, module_overview, module_overview.py
- **community 129** (2 nodes): Playground, Playground.tsx
- **community 131** (5 nodes): SolarOrb, SolarOrb.tsx, SolarOrbProps, Star, hexToGlow
- **community 135** (3 nodes): AppShell, AppShell.tsx, AppShellProps
- **community 136** (3 nodes): Badge, Badge.tsx, BadgeProps
- **community 137** (3 nodes): BootStep, BootStep.tsx, BootStepProps
- **community 138** (2 nodes): Button.tsx, ButtonProps
- **community 139** (5 nodes): Card, Card.tsx, CardHeader, CardHeaderProps, CardProps
- **community 140** (3 nodes): Chip, Chip.tsx, ChipProps
- **community 141** (5 nodes): CountUp, CountUp.tsx, CountUpProps, formatNumber, step
- **community 142** (3 nodes): Divider, Divider.tsx, DividerProps
- **community 143** (3 nodes): HudCorners, HudCorners.tsx, HudCornersProps
- **community 144** (3 nodes): Icon, Icon.tsx, IconProps
- **community 145** (4 nodes): IconRail, IconRail.tsx, IconRailItem, IconRailProps
- **community 146** (2 nodes): Input.tsx, InputProps
- **community 147** (3 nodes): Kbd, Kbd.tsx, KbdProps
- **community 148** (3 nodes): LiveDot, LiveDot.tsx, LiveDotProps
- **community 149** (4 nodes): AntonMark, Logo, Logo.tsx, LogoProps
- **community 150** (3 nodes): MicIndicator, MicIndicator.tsx, MicIndicatorProps
- **community 151** (12 nodes): PrefControls.tsx, PrefInput, PrefInputProps, PrefOption, PrefSeg, PrefSegProps, PrefSelect, PrefSelectProps, PrefSlider, PrefSliderProps, PrefTog, PrefTogProps
- **community 152** (3 nodes): PrefGroup, PrefGroup.tsx, PrefGroupProps
- **community 153** (3 nodes): PrefRow, PrefRow.tsx, PrefRowProps
- **community 154** (3 nodes): ProgressBar, ProgressBar.tsx, ProgressBarProps
- **community 155** (3 nodes): RiskBars, RiskBars.tsx, RiskBarsProps
- **community 156** (4 nodes): SearchBox, SearchBox.tsx, SearchBoxProps, handle
- **community 157** (4 nodes): SegmentedControl, SegmentedControl.tsx, SegmentedControlProps, SegmentedOption
- **community 158** (3 nodes): Sparkline, Sparkline.tsx, SparklineProps
- **community 159** (3 nodes): Stat, Stat.tsx, StatProps
- **community 160** (3 nodes): Swatches, Swatches.tsx, SwatchesProps
- **community 161** (7 nodes): PersistShape, ThemeProvider, ThemeProvider.tsx, ThemeProviderProps, ThemeState, readPersisted, writePersisted
- **community 162** (4 nodes): TopBar, TopBar.tsx, TopBarNavItem, TopBarProps
- **community 163** (3 nodes): VoiceDock, VoiceDock.tsx, VoiceDockProps
- **community 164** (3 nodes): WatchRow, WatchRow.tsx, WatchRowProps
- **community 165** (3 nodes): Waveform, Waveform.tsx, WaveformProps
- **community 166** (12 nodes): Notification, Notification.tsx, Props, beginExit, cancelTtl, dismissNotification, fmtDateTime, fmtTime, notifications.icons.tsx, notify.ts, severityIcon, startTtl
- **community 167** (4 nodes): NotificationsHost, NotificationsHost.tsx, NotificationsHostProps, useNotifications
- **community 169** (8 nodes): clearNotifications, defaultTtl, emit, getServerSnapshot, getSnapshot, nextId, notifications.store.ts, pushNotification
- **community 170** (4 nodes): Notification, NotificationAction, NotificationInput, notifications.types.ts
- **community 174** (2 nodes): onSuccess, tsup.config.ts
- **community 175** (3 nodes): _probe_auth.py, _vault_secret, probe_credentials
- **community 177** (2 nodes): _record, run
- **community 178** (2 nodes): _check_popup_fits, _record
- **community 184** (2 nodes): doc-per-code-change, files-max-100-lines
