# Fux GRAPH_REPORT

_1615 nodes · 7465 edges · 360 code files · 40 rules · 198 communities._

## Node types

- function: 973
- code-file: 360
- class: 242
- convention: 11
- narrative: 11
- glossary: 8
- memory: 4
- regulatory: 2
- formula: 2
- invariant: 1
- rule: 1

## Edges

_4119 of 7465 are INFERRED (low-confidence `references`, down-weighted in clustering/centrality)._

- references: 4119
- calls: 2034
- contains: 1217
- related: 63
- governs: 32

## God nodes (highest connectivity)

- **get** (function) — 161 edges
- **run** (function) — 79 edges
- **angelone_dump.py** (code-file) — 76 edges
- **binance_dump.py** (code-file) — 76 edges
- **groww_dump.py** (code-file) — 76 edges
- **indmoney_dump.py** (code-file) — 76 edges
- **tickertape_dump.py** (code-file) — 76 edges
- **zerodha_coin_dump.py** (code-file) — 76 edges
- **zerodha_kite_dump.py** (code-file) — 76 edges
- **cerebras.py** (code-file) — 76 edges
- **groq.py** (code-file) — 76 edges
- **mistral.py** (code-file) — 76 edges

## Chokepoints (PageRank centrality)

- **get** (function) — 0.0136
- **ChatRail.tsx** (code-file) — 0.0053
- **AlphaBar.tsx** (code-file) — 0.0044
- **info** (function) — 0.0042
- **post** (function) — 0.0040
- **portfolio.types.ts** (code-file) — 0.0036
- **PrefControls.tsx** (code-file) — 0.0036
- **test_brokers.py** (code-file) — 0.0035
- **fetch** (function) — 0.0031
- **fetch** (function) — 0.0030
- **portfolio.query.ts** (code-file) — 0.0030
- **auth.types.ts** (code-file) — 0.0027

## Communities

- **community 0** (4 nodes): do_run_migrations, env.py, run_migrations_offline, run_migrations_online
- **community 1** (4 nodes): 1d8f1014a7d4_dashboard_ticker_watchlist_items.py, _table, downgrade, upgrade
- **community 2** (12 nodes): 640eee61bc50_initial_schema_with_pgvector_memory.py, Text, Text.tsx, TextProps, a3c9f2e1b4d7_iam_tables.py, b3d6f8a2c9e1_remove_iam_tables.py, downgrade, downgrade, downgrade, upgrade, upgrade, upgrade
- **community 5** (3 nodes): Settings, _validate_secrets, config.py
- **community 6** (3 nodes): Base, database.py, get_db
- **community 7** (7 nodes): UserClaims, decode_access_token, deps.py, get_current_user, require_owner, security.py, user_from_jwt
- **community 8** (4 nodes): _repo_root, env_loader.py, get_env_files, load_env_files
- **community 10** (10 nodes): create_app, lifespan, logger.py, logging.py, main.py, setup_logging, setup_logging, test_log_writes_to_file, test_logger.py, test_setup_logging_creates_dir
- **community 11** (725 nodes): AngelOneSource, AssetClass, Base, BinanceSource, BraveSource, BrokerSource, BseAnnouncementsSource, CerebrasAdapter, ClaudeSdkAdapter, CompleteIn, ComposeRequest, ComposeResponse
- **community 14** (6 nodes): _cache_root, _check_dev_host, _fernet, _http.py, load_session, save_session
- **community 15** (38 nodes): AllocationSlice, HoldingsAggregator, RebalanceDrift, RebalanceSuggestion, TreemapCell, TreemapCell, TreemapCell.tsx, TreemapCellProps, _inr_invested, _inr_value, aggregator.py, aggregator_types.py
- **community 17** (38 nodes): AccountSection, AlphaSection, AlphaSection.tsx, AlphaSectionProps, AppearanceSection, AppearanceSection.tsx, AppearanceSectionProps, DisplaySection, DisplaySection.tsx, DisplaySectionProps, MarketsSection, MarketsSection.tsx
- **community 18** (12 nodes): _is_due, _prime_one, _prime_unsynced, _refetch_loop, _sync_one, _sync_one, boot_sync_stream, generate, health_routes.py, refetch.py, start_refetch_loop, sync
- **community 20** (4 nodes): _as_cash, cash_routes.py, get_cash, sync_one_cash
- **community 21** (7 nodes): _fetch_live_usd_inr, _load_cached, _path, _read_all, _write_row, fx.py, get_inr_per_usd
- **community 24** (2 nodes): _to_float, normalize
- **community 26** (5 nodes): Treemap, Treemap.tsx, _worst, squarify, treemap_helper.py
- **community 27** (5 nodes): WalletInfo, _aggregate_holdings, _build_one, list_wallets, wallet_aggregator.py
- **community 31** (3 nodes): _vocab, build_system, compose_prompt.py
- **community 32** (3 nodes): ChatMessage, ChatRequest, concierge_schemas.py
- **community 33** (7 nodes): _bin, _run, fux_bridge.py, recall, record_feedback, registry, validate
- **community 35** (16 nodes): DashboardTickerItem, DashboardWatchlistItem, _now, _seed_ticker, _seed_watchlist, add, add_ticker, add_watchlist, dashboard_models.py, dashboard_repo.py, delete_ticker, delete_watchlist
- **community 36** (24 nodes): BriefBlock, CreateTickerItemRequest, CreateWatchlistItemRequest, DashboardStats, RiskMeter, StatCard, TerminalBrief, TickerItem, TickerItem, WatchlistItem, _fmt_inr_short, _ticker_dto
- **community 39** (15 nodes): BootReport, BootReport, BootService, BootService, BootStatus, SyncResult, _broker_detail, boot.types.ts, boot_probes.py, boot_report, boot_schemas.py, probe_backend
- **community 41** (3 nodes): _forward, iam_proxy, iam_proxy.py
- **community 44** (3 nodes): Order, Watchlist, portfolio_models.py
- **community 46** (2 nodes): _make_holding, _seed_zerodha
- **community 47** (12 nodes): README.md, async-everywhere, compose.registry.ts, concierge-default-model, concierge-registry-single-source, doc-per-code-change, files-max-100-lines, orff, project-fux, providers.json, routing.json, ui-component-contract
- **community 55** (2 nodes): gen-concierge-registry.mjs, lit
- **community 56** (2 nodes): RootLayout, layout.tsx
- **community 57** (7 nodes): ChatProvider, LoginPage, WatchlistCard.tsx, getMe, handleSubmit, page.tsx, submit
- **community 58** (2 nodes): Home, page.tsx
- **community 59** (23 nodes): AssetClassCounts, FilterBar, FilterBar.tsx, FilterBarProps, FilterState, PortfolioHeader, PortfolioHeader.tsx, PortfolioPage, applyFilter, assetClassCounts, bucketOf, equitySubOf
- **community 60** (2 nodes): PreferencesPage, page.tsx
- **community 61** (2 nodes): AxiosRequestConfig, api.ts
- **community 62** (12 nodes): ApiError, QueryProvider, Register, apiError.ts, apiNotify.ts, extractDetail, isApiError, kindFromStatus, notifyApiError, providers.tsx, shouldRetry, toApiError
- **community 63** (2 nodes): AppState, store.ts
- **community 65** (9 nodes): _importPublicKey, _pemToBytes, auth.api.ts, deleteApiKey, encryptCredentials, getLoginKey, invalidateLoginKey, loginUser, verifyModeSignature
- **community 66** (18 nodes): ActionBtn, DangerButton, PrivacySection, PrivacySection.tsx, PrivacySectionProps, SessionsGroup, SessionsGroup.tsx, SignOutBtn, auth.query.ts, device, fmt, handleLogout
- **community 67** (2 nodes): AuthGuard, auth.guard.tsx
- **community 68** (9 nodes): ApiKey, ApiKeyCreateRequest, IamUser, LoginKeyResponse, LoginRequest, RegisterRequest, SessionResponse, TokenResponse, auth.types.ts
- **community 69** (7 nodes): AuthState, applyHeader, errorMessage, errorStatus, requestPath, skipRefreshRetry, useAuthStore.ts
- **community 70** (18 nodes): AlphaBar, AlphaBar.tsx, Bars, ChatCommandLine, ChatIcon, CollapsedStrip, ComposeCard, Kbd, MicIcon, ModeBtn, ModeSegment, Props
- **community 71** (4 nodes): ChatContext.tsx, ChatCtx, loadChoice, useChat
- **community 72** (23 nodes): ChatNavIcon, ChatRail, ChatRail.tsx, ClockIcon, CrBtn, EmptyState, FuChip, InlineTokens, Kbd, MicNavIcon, NavBtn, Props
- **community 73** (3 nodes): DynamicRenderer, DynamicRenderer.tsx, Props
- **community 74** (9 nodes): ActiveDot, AutoRow, AutoRowProps, ModelPicker.rows.tsx, ModelRow, ModelRowProps, ProvRow, ProvRowProps, Tag
- **community 76** (4 nodes): ModelPicker.tsx, Props, onKey, onMouseDown
- **community 77** (12 nodes): ActiveModel, ChatTurn, ModelPicker, Resolved, activeModelFor, classifyIntent, concierge.routing.ts, concierge.types.ts, lookup, providerDefault, resolveProviderAuto, resolveTopAuto
- **community 78** (4 nodes): MicToggle, Props, VoiceCenter.tsx, Waveform
- **community 79** (5 nodes): DefaultChoice, concierge.defaults.ts, ctxScore, pickDefaultChoice, score
- **community 81** (4 nodes): IntentPattern, ModelMeta, ProviderMeta, concierge.registry.generated.ts
- **community 83** (7 nodes): SRErrorEvent, SREvent, SRResult, SRResultList, WebkitSR, getSRCtor, webspeech.types.ts
- **community 84** (3 nodes): AlphaBriefCard, AlphaBriefCard.tsx, useDashboardBrief
- **community 85** (17 nodes): BlockingBoot, BootGate, BootGate.tsx, announce, diagnose, emitProgress, fetchBootReport, isBlocking, isBrokerRow, isCached, reloadAction, runSync
- **community 86** (4 nodes): BootScreen, BootScreen.tsx, BootScreenProps, BootStep
- **community 87** (2 nodes): MarketOverview, MarketOverview.tsx
- **community 88** (2 nodes): OrbStage, OrbStage.tsx
- **community 89** (3 nodes): TerminalRail, TerminalRail.tsx, isActive
- **community 90** (3 nodes): TerminalStats, TerminalStats.tsx, useDashboardStats
- **community 91** (5 nodes): TerminalTicker, TerminalTicker.tsx, useAddTickerItem, useDashboardTicker, useDeleteTickerItem
- **community 92** (4 nodes): TerminalTopBar, TerminalTopBar.tsx, handleLogout, isActive
- **community 93** (2 nodes): TerminalVoice, TerminalVoice.tsx
- **community 94** (2 nodes): Watchlist, Watchlist.tsx
- **community 95** (6 nodes): WatchlistCard, dashboard.query.ts, useAddWatchlistItem, useDashboardRisk, useDashboardWatchlist, useDeleteWatchlistItem
- **community 96** (6 nodes): Diagnosis, Failure, Pattern, boot.diagnose.ts, copyAndConfirm, plural
- **community 97** (8 nodes): BriefBlockDTO, DashboardStatsDTO, RiskMeterDTO, StatCardDTO, TerminalBriefDTO, TickerItemDTO, WatchlistItemDTO, dashboard.types.ts
- **community 99** (5 nodes): AssetClassFilter, AssetClassFilter.tsx, AssetClassFilterProps, ChipGroup, ChipGroupProps
- **community 100** (4 nodes): ColDef, Ledger, Ledger.tsx, LedgerProps
- **community 101** (27 nodes): LedgerRow, LedgerRow.tsx, PortfolioCompactBar, PortfolioCompactBar.tsx, PortfolioCompactBarProps, SourceSpotlight, SummaryBar, SummaryBar.tsx, SummaryBarProps, WalletCard, WalletCard.tsx, WalletCardProps
- **community 102** (2 nodes): PnLToggle, PnLToggle.tsx
- **community 103** (4 nodes): RebalanceRail, RebalanceRail.tsx, RebalanceRailProps, useRebalance
- **community 104** (5 nodes): SortMenu, SortMenu.tsx, SortMenuProps, h, pick
- **community 105** (3 nodes): Props, SourceActions, SourceActions.tsx
- **community 106** (3 nodes): Props, SourceOtpDialog, SourceOtpDialog.tsx
- **community 107** (5 nodes): SourceRow, SourceRow.tsx, formatTime, sources.utils.ts, statusVariant
- **community 108** (4 nodes): SourceSpotlight.tsx, SourceSpotlightProps, SpotStat, onRefresh
- **community 109** (12 nodes): SourcesPanel, SourcesPanel.tsx, handleReset, handleStartLogin, handleSubmitOtp, handleSync, handleSyncAll, onAfter, readErr, useSourceRow.hook.ts, useSources, useSyncAll
- **community 110** (10 nodes): StripButton, WalletStrip, WalletStrip.tsx, WalletStripProps, handleForceRefresh, handleRefreshHoldings, handleSyncCash, useForceRefresh, useSyncAllSources, useSyncAllWallets
- **community 112** (8 nodes): FxResponseDTO, portfolio.query.ts, useResetSource, useSourceRow, useStartLogin, useSubmitOtp, useSyncSource, useTreemap
- **community 113** (12 nodes): AllocationSliceDTO, HoldingDTO, HoldingsResponseDTO, PortfolioTotalsDTO, RebalanceResponseDTO, SourceInfoDTO, SyncAllResultDTO, TreemapCellDTO, TreemapResponseDTO, WalletInfoDTO, WalletsResponseDTO, portfolio.types.ts
- **community 114** (5 nodes): Rect, aspectRatio, squarify, treemap.utils.ts, worstAspect
- **community 115** (4 nodes): AboutSection, AboutSection.tsx, AboutSectionProps, StaticBox
- **community 116** (3 nodes): AccountSection.tsx, AccountSectionProps, Hotkey
- **community 117** (7 nodes): PreferencesScreen.tsx, PreferencesSidebar, PreferencesSidebar.tsx, PreferencesSidebarProps, isDeepEqual, modifiedCount, onKey
- **community 118** (2 nodes): SectionIcon, SectionIcon.tsx
- **community 119** (3 nodes): StubSection, StubSection.tsx, StubSectionProps
- **community 121** (2 nodes): PrefSectionMeta, preferences.types.ts
- **community 122** (2 nodes): ScreenerPanel, ScreenerPanel.tsx
- **community 125** (9 nodes): Chunk, _chunk_markdown, _chunk_python, _chunk_ts_like, _chunk_window, chunk_file, chunker.py, content_hash, detect_lang
- **community 127** (3 nodes): _row_dict, get_symbol, get_symbol.py
- **community 128** (3 nodes): _walk_up, module_overview, module_overview.py
- **community 133** (2 nodes): Playground, Playground.tsx
- **community 135** (5 nodes): SolarOrb, SolarOrb.tsx, SolarOrbProps, Star, hexToGlow
- **community 139** (3 nodes): AppShell, AppShell.tsx, AppShellProps
- **community 140** (3 nodes): Badge, Badge.tsx, BadgeProps
- **community 141** (3 nodes): BootStep, BootStep.tsx, BootStepProps
- **community 142** (2 nodes): Button.tsx, ButtonProps
- **community 143** (5 nodes): Card, Card.tsx, CardHeader, CardHeaderProps, CardProps
- **community 144** (3 nodes): Chip, Chip.tsx, ChipProps
- **community 145** (5 nodes): CountUp, CountUp.tsx, CountUpProps, formatNumber, step
- **community 146** (3 nodes): Divider, Divider.tsx, DividerProps
- **community 147** (3 nodes): HudCorners, HudCorners.tsx, HudCornersProps
- **community 148** (3 nodes): Icon, Icon.tsx, IconProps
- **community 149** (4 nodes): IconRail, IconRail.tsx, IconRailItem, IconRailProps
- **community 150** (2 nodes): Input.tsx, InputProps
- **community 151** (3 nodes): Kbd, Kbd.tsx, KbdProps
- **community 152** (3 nodes): LiveDot, LiveDot.tsx, LiveDotProps
- **community 153** (4 nodes): AntonMark, Logo, Logo.tsx, LogoProps
- **community 154** (3 nodes): MicIndicator, MicIndicator.tsx, MicIndicatorProps
- **community 155** (12 nodes): PrefControls.tsx, PrefInput, PrefInputProps, PrefOption, PrefSeg, PrefSegProps, PrefSelect, PrefSelectProps, PrefSlider, PrefSliderProps, PrefTog, PrefTogProps
- **community 156** (3 nodes): PrefGroup, PrefGroup.tsx, PrefGroupProps
- **community 157** (3 nodes): PrefRow, PrefRow.tsx, PrefRowProps
- **community 158** (3 nodes): ProgressBar, ProgressBar.tsx, ProgressBarProps
- **community 159** (3 nodes): RiskBars, RiskBars.tsx, RiskBarsProps
- **community 160** (4 nodes): SearchBox, SearchBox.tsx, SearchBoxProps, handle
- **community 161** (4 nodes): SegmentedControl, SegmentedControl.tsx, SegmentedControlProps, SegmentedOption
- **community 162** (3 nodes): Sparkline, Sparkline.tsx, SparklineProps
- **community 163** (3 nodes): Stat, Stat.tsx, StatProps
- **community 164** (3 nodes): Swatches, Swatches.tsx, SwatchesProps
- **community 165** (7 nodes): PersistShape, ThemeProvider, ThemeProvider.tsx, ThemeProviderProps, ThemeState, readPersisted, writePersisted
- **community 166** (4 nodes): TopBar, TopBar.tsx, TopBarNavItem, TopBarProps
- **community 167** (3 nodes): VoiceDock, VoiceDock.tsx, VoiceDockProps
- **community 168** (3 nodes): WatchRow, WatchRow.tsx, WatchRowProps
- **community 169** (3 nodes): Waveform, Waveform.tsx, WaveformProps
- **community 170** (12 nodes): Notification, Notification.tsx, Props, beginExit, cancelTtl, dismissNotification, fmtDateTime, fmtTime, notifications.icons.tsx, notify.ts, severityIcon, startTtl
- **community 171** (4 nodes): NotificationsHost, NotificationsHost.tsx, NotificationsHostProps, useNotifications
- **community 173** (8 nodes): clearNotifications, defaultTtl, emit, getServerSnapshot, getSnapshot, nextId, notifications.store.ts, pushNotification
- **community 174** (4 nodes): Notification, NotificationAction, NotificationInput, notifications.types.ts
- **community 178** (2 nodes): onSuccess, tsup.config.ts
- **community 179** (7 nodes): Probes.md, WHY_PROBES_NOT_MCP.md, broker-source-integration, cdp-chrome, enctoken, probe-cdp-not-playwright, project-cdp-prerequisite
- **community 180** (3 nodes): _probe_auth.py, _vault_secret, probe_credentials
- **community 182** (2 nodes): _record, run
- **community 183** (2 nodes): _record, run
- **community 184** (2 nodes): _check_popup_fits, _record
- **community 185** (4 nodes): afbach-vault, no-secrets-in-vcs, project-wagner-dante, vault-only-credentials
