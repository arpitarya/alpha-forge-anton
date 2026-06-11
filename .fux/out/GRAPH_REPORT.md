# Fux GRAPH_REPORT

_1652 nodes · 7778 edges · 368 code files · 43 rules · 204 communities._

## Node types

- function: 996
- code-file: 368
- class: 245
- narrative: 14
- convention: 11
- glossary: 8
- memory: 4
- regulatory: 2
- formula: 2
- invariant: 1
- rule: 1

## Edges

_4265 of 7778 are INFERRED (low-confidence `references`, down-weighted in clustering/centrality)._

- references: 4265
- calls: 2172
- contains: 1243
- related: 63
- governs: 35

## God nodes (highest connectivity)

- **get** (function) — 172 edges
- **run** (function) — 80 edges
- **angelone_dump.py** (code-file) — 79 edges
- **binance_dump.py** (code-file) — 79 edges
- **groww_dump.py** (code-file) — 79 edges
- **indmoney_dump.py** (code-file) — 79 edges
- **tickertape_dump.py** (code-file) — 79 edges
- **zerodha_coin_dump.py** (code-file) — 79 edges
- **zerodha_kite_dump.py** (code-file) — 79 edges
- **angelone_probe.py** (code-file) — 76 edges
- **binance_probe.py** (code-file) — 76 edges
- **indmoney_probe.py** (code-file) — 76 edges

## Chokepoints (PageRank centrality)

- **get** (function) — 0.0140
- **ChatRail.tsx** (code-file) — 0.0052
- **AlphaBar.tsx** (code-file) — 0.0043
- **info** (function) — 0.0041
- **post** (function) — 0.0039
- **portfolio.types.ts** (code-file) — 0.0035
- **PrefControls.tsx** (code-file) — 0.0035
- **test_brokers.py** (code-file) — 0.0035
- **fetch** (function) — 0.0030
- **fetch** (function) — 0.0030
- **portfolio.query.ts** (code-file) — 0.0029
- **auth.types.ts** (code-file) — 0.0026

## Communities

- **community 0** (4 nodes): do_run_migrations, env.py, run_migrations_offline, run_migrations_online
- **community 1** (4 nodes): 1d8f1014a7d4_dashboard_ticker_watchlist_items.py, _table, downgrade, upgrade
- **community 2** (12 nodes): 640eee61bc50_initial_schema_with_pgvector_memory.py, Text, Text.tsx, TextProps, a3c9f2e1b4d7_iam_tables.py, b3d6f8a2c9e1_remove_iam_tables.py, downgrade, downgrade, downgrade, upgrade, upgrade, upgrade
- **community 5** (3 nodes): Settings, _validate_secrets, config.py
- **community 6** (3 nodes): Base, database.py, get_db
- **community 7** (7 nodes): UserClaims, decode_access_token, deps.py, get_current_user, require_owner, security.py, user_from_jwt
- **community 8** (4 nodes): _repo_root, env_loader.py, get_env_files, load_env_files
- **community 10** (10 nodes): create_app, lifespan, logger.py, logging.py, main.py, setup_logging, setup_logging, test_log_writes_to_file, test_logger.py, test_setup_logging_creates_dir
- **community 11** (702 nodes): AngelOneSource, AssetClass, Base, BinanceSource, BraveSource, BrokerSource, BseAnnouncementsSource, CerebrasAdapter, ClaudeSdkAdapter, CompleteIn, ComposeRequest, ComposeResponse
- **community 14** (6 nodes): _cache_root, _check_dev_host, _fernet, _http.py, load_session, save_session
- **community 15** (53 nodes): AllocationSlice, ClassDrift, HoldingsAggregator, Plan, RebalanceDrift, RebalanceSuggestion, TreemapCell, TreemapCell, TreemapCell.tsx, TreemapCellProps, _inr_invested, _inr_value
- **community 17** (38 nodes): AccountSection, AlphaSection, AlphaSection.tsx, AlphaSectionProps, AppearanceSection, AppearanceSection.tsx, AppearanceSectionProps, DisplaySection, DisplaySection.tsx, DisplaySectionProps, MarketsSection, MarketsSection.tsx
- **community 18** (12 nodes): _is_due, _prime_one, _prime_unsynced, _refetch_loop, _sync_one, _sync_one, boot_sync_stream, generate, health_routes.py, refetch.py, start_refetch_loop, sync
- **community 20** (4 nodes): _as_cash, cash_routes.py, get_cash, sync_one_cash
- **community 21** (7 nodes): _fetch_live_usd_inr, _load_cached, _path, _read_all, _write_row, fx.py, get_inr_per_usd
- **community 24** (2 nodes): _to_float, normalize
- **community 25** (32 nodes): NewsItem, NewsItemResponse, _extract, _fetch, _intents, _load, _providers, _routing, classify_intent, ctx_score, default_choice, default_policy
- **community 27** (5 nodes): Treemap, Treemap.tsx, _worst, squarify, treemap_helper.py
- **community 28** (5 nodes): WalletInfo, _aggregate_holdings, _build_one, list_wallets, wallet_aggregator.py
- **community 32** (3 nodes): _vocab, build_system, compose_prompt.py
- **community 33** (3 nodes): ChatMessage, ChatRequest, concierge_schemas.py
- **community 34** (7 nodes): _bin, _run, fux_bridge.py, recall, record_feedback, registry, validate
- **community 36** (16 nodes): DashboardTickerItem, DashboardWatchlistItem, _now, _seed_ticker, _seed_watchlist, add, add_ticker, add_watchlist, dashboard_models.py, dashboard_repo.py, delete_ticker, delete_watchlist
- **community 37** (24 nodes): BriefBlock, CreateTickerItemRequest, CreateWatchlistItemRequest, DashboardStats, RiskMeter, StatCard, TerminalBrief, TickerItem, TickerItem, WatchlistItem, _fmt_inr_short, _ticker_dto
- **community 40** (15 nodes): BootReport, BootReport, BootService, BootService, BootStatus, SyncResult, _broker_detail, boot.types.ts, boot_probes.py, boot_report, boot_schemas.py, probe_backend
- **community 42** (3 nodes): _forward, iam_proxy, iam_proxy.py
- **community 45** (3 nodes): Order, Watchlist, portfolio_models.py
- **community 47** (2 nodes): _make_holding, _seed_zerodha
- **community 48** (6 nodes): provider_slugs, test_chains_reference_known_providers, test_classify_intent, test_concierge_registry.py, test_every_provider_has_at_least_one_model, test_provider_slug_literal_matches_registry
- **community 49** (12 nodes): README.md, async-everywhere, compose.registry.ts, concierge-default-model, concierge-registry-single-source, doc-per-code-change, files-max-100-lines, orff, project-fux, providers.json, routing.json, ui-component-contract
- **community 57** (2 nodes): gen-concierge-registry.mjs, lit
- **community 58** (2 nodes): RootLayout, layout.tsx
- **community 59** (7 nodes): ChatProvider, LoginPage, WatchlistCard.tsx, getMe, handleSubmit, page.tsx, submit
- **community 60** (2 nodes): Home, page.tsx
- **community 61** (23 nodes): AssetClassCounts, FilterBar, FilterBar.tsx, FilterBarProps, FilterState, PortfolioHeader, PortfolioHeader.tsx, PortfolioPage, applyFilter, assetClassCounts, bucketOf, equitySubOf
- **community 62** (2 nodes): PreferencesPage, page.tsx
- **community 63** (2 nodes): AxiosRequestConfig, api.ts
- **community 64** (12 nodes): ApiError, QueryProvider, Register, apiError.ts, apiNotify.ts, extractDetail, isApiError, kindFromStatus, notifyApiError, providers.tsx, shouldRetry, toApiError
- **community 65** (2 nodes): AppState, store.ts
- **community 67** (9 nodes): _importPublicKey, _pemToBytes, auth.api.ts, deleteApiKey, encryptCredentials, getLoginKey, invalidateLoginKey, loginUser, verifyModeSignature
- **community 68** (18 nodes): ActionBtn, DangerButton, PrivacySection, PrivacySection.tsx, PrivacySectionProps, SessionsGroup, SessionsGroup.tsx, SignOutBtn, auth.query.ts, device, fmt, handleLogout
- **community 69** (2 nodes): AuthGuard, auth.guard.tsx
- **community 70** (9 nodes): ApiKey, ApiKeyCreateRequest, IamUser, LoginKeyResponse, LoginRequest, RegisterRequest, SessionResponse, TokenResponse, auth.types.ts
- **community 71** (7 nodes): AuthState, applyHeader, errorMessage, errorStatus, requestPath, skipRefreshRetry, useAuthStore.ts
- **community 72** (18 nodes): AlphaBar, AlphaBar.tsx, Bars, ChatCommandLine, ChatIcon, CollapsedStrip, ComposeCard, Kbd, MicIcon, ModeBtn, ModeSegment, Props
- **community 73** (4 nodes): ChatContext.tsx, ChatCtx, loadChoice, useChat
- **community 74** (23 nodes): ChatNavIcon, ChatRail, ChatRail.tsx, ClockIcon, CrBtn, EmptyState, FuChip, InlineTokens, Kbd, MicNavIcon, NavBtn, Props
- **community 75** (3 nodes): DynamicRenderer, DynamicRenderer.tsx, Props
- **community 76** (9 nodes): ActiveDot, AutoRow, AutoRowProps, ModelPicker.rows.tsx, ModelRow, ModelRowProps, ProvRow, ProvRowProps, Tag
- **community 78** (4 nodes): ModelPicker.tsx, Props, onKey, onMouseDown
- **community 79** (12 nodes): ActiveModel, ChatTurn, ModelPicker, Resolved, activeModelFor, classifyIntent, concierge.routing.ts, concierge.types.ts, lookup, providerDefault, resolveProviderAuto, resolveTopAuto
- **community 80** (4 nodes): MicToggle, Props, VoiceCenter.tsx, Waveform
- **community 81** (5 nodes): DefaultChoice, concierge.defaults.ts, ctxScore, pickDefaultChoice, score
- **community 83** (5 nodes): IntentPattern, ModelConsumption, ModelMeta, ProviderMeta, concierge.registry.generated.ts
- **community 85** (7 nodes): SRErrorEvent, SREvent, SRResult, SRResultList, WebkitSR, getSRCtor, webspeech.types.ts
- **community 86** (3 nodes): AlphaBriefCard, AlphaBriefCard.tsx, useDashboardBrief
- **community 87** (17 nodes): BlockingBoot, BootGate, BootGate.tsx, announce, diagnose, emitProgress, fetchBootReport, isBlocking, isBrokerRow, isCached, reloadAction, runSync
- **community 88** (4 nodes): BootScreen, BootScreen.tsx, BootScreenProps, BootStep
- **community 89** (2 nodes): MarketOverview, MarketOverview.tsx
- **community 90** (2 nodes): OrbStage, OrbStage.tsx
- **community 91** (3 nodes): TerminalRail, TerminalRail.tsx, isActive
- **community 92** (3 nodes): TerminalStats, TerminalStats.tsx, useDashboardStats
- **community 93** (5 nodes): TerminalTicker, TerminalTicker.tsx, useAddTickerItem, useDashboardTicker, useDeleteTickerItem
- **community 94** (4 nodes): TerminalTopBar, TerminalTopBar.tsx, handleLogout, isActive
- **community 95** (2 nodes): TerminalVoice, TerminalVoice.tsx
- **community 96** (2 nodes): Watchlist, Watchlist.tsx
- **community 97** (6 nodes): WatchlistCard, dashboard.query.ts, useAddWatchlistItem, useDashboardRisk, useDashboardWatchlist, useDeleteWatchlistItem
- **community 98** (6 nodes): Diagnosis, Failure, Pattern, boot.diagnose.ts, copyAndConfirm, plural
- **community 99** (8 nodes): BriefBlockDTO, DashboardStatsDTO, RiskMeterDTO, StatCardDTO, TerminalBriefDTO, TickerItemDTO, WatchlistItemDTO, dashboard.types.ts
- **community 101** (5 nodes): AssetClassFilter, AssetClassFilter.tsx, AssetClassFilterProps, ChipGroup, ChipGroupProps
- **community 102** (4 nodes): ColDef, Ledger, Ledger.tsx, LedgerProps
- **community 103** (27 nodes): LedgerRow, LedgerRow.tsx, PortfolioCompactBar, PortfolioCompactBar.tsx, PortfolioCompactBarProps, SourceSpotlight, SummaryBar, SummaryBar.tsx, SummaryBarProps, WalletCard, WalletCard.tsx, WalletCardProps
- **community 104** (2 nodes): PnLToggle, PnLToggle.tsx
- **community 105** (4 nodes): RebalanceRail, RebalanceRail.tsx, RebalanceRailProps, useRebalance
- **community 106** (5 nodes): SortMenu, SortMenu.tsx, SortMenuProps, h, pick
- **community 107** (3 nodes): Props, SourceActions, SourceActions.tsx
- **community 108** (3 nodes): Props, SourceOtpDialog, SourceOtpDialog.tsx
- **community 109** (5 nodes): SourceRow, SourceRow.tsx, formatTime, sources.utils.ts, statusVariant
- **community 110** (4 nodes): SourceSpotlight.tsx, SourceSpotlightProps, SpotStat, onRefresh
- **community 111** (12 nodes): SourcesPanel, SourcesPanel.tsx, handleReset, handleStartLogin, handleSubmitOtp, handleSync, handleSyncAll, onAfter, readErr, useSourceRow.hook.ts, useSources, useSyncAll
- **community 112** (10 nodes): StripButton, WalletStrip, WalletStrip.tsx, WalletStripProps, handleForceRefresh, handleRefreshHoldings, handleSyncCash, useForceRefresh, useSyncAllSources, useSyncAllWallets
- **community 114** (8 nodes): FxResponseDTO, portfolio.query.ts, useResetSource, useSourceRow, useStartLogin, useSubmitOtp, useSyncSource, useTreemap
- **community 115** (12 nodes): AllocationSliceDTO, HoldingDTO, HoldingsResponseDTO, PortfolioTotalsDTO, RebalanceResponseDTO, SourceInfoDTO, SyncAllResultDTO, TreemapCellDTO, TreemapResponseDTO, WalletInfoDTO, WalletsResponseDTO, portfolio.types.ts
- **community 116** (5 nodes): Rect, aspectRatio, squarify, treemap.utils.ts, worstAspect
- **community 117** (4 nodes): AboutSection, AboutSection.tsx, AboutSectionProps, StaticBox
- **community 118** (3 nodes): AccountSection.tsx, AccountSectionProps, Hotkey
- **community 119** (7 nodes): PreferencesScreen.tsx, PreferencesSidebar, PreferencesSidebar.tsx, PreferencesSidebarProps, isDeepEqual, modifiedCount, onKey
- **community 120** (2 nodes): SectionIcon, SectionIcon.tsx
- **community 121** (3 nodes): StubSection, StubSection.tsx, StubSectionProps
- **community 123** (2 nodes): PrefSectionMeta, preferences.types.ts
- **community 124** (2 nodes): ScreenerPanel, ScreenerPanel.tsx
- **community 127** (9 nodes): Chunk, _chunk_markdown, _chunk_python, _chunk_ts_like, _chunk_window, chunk_file, chunker.py, content_hash, detect_lang
- **community 129** (3 nodes): _row_dict, get_symbol, get_symbol.py
- **community 130** (3 nodes): _walk_up, module_overview, module_overview.py
- **community 133** (3 nodes): _canonical_url, _compute_hash, types.py
- **community 136** (2 nodes): Playground, Playground.tsx
- **community 138** (5 nodes): SolarOrb, SolarOrb.tsx, SolarOrbProps, Star, hexToGlow
- **community 142** (3 nodes): AppShell, AppShell.tsx, AppShellProps
- **community 143** (3 nodes): Badge, Badge.tsx, BadgeProps
- **community 144** (3 nodes): BootStep, BootStep.tsx, BootStepProps
- **community 145** (2 nodes): Button.tsx, ButtonProps
- **community 146** (5 nodes): Card, Card.tsx, CardHeader, CardHeaderProps, CardProps
- **community 147** (3 nodes): Chip, Chip.tsx, ChipProps
- **community 148** (5 nodes): CountUp, CountUp.tsx, CountUpProps, formatNumber, step
- **community 149** (3 nodes): Divider, Divider.tsx, DividerProps
- **community 150** (3 nodes): HudCorners, HudCorners.tsx, HudCornersProps
- **community 151** (3 nodes): Icon, Icon.tsx, IconProps
- **community 152** (4 nodes): IconRail, IconRail.tsx, IconRailItem, IconRailProps
- **community 153** (2 nodes): Input.tsx, InputProps
- **community 154** (3 nodes): Kbd, Kbd.tsx, KbdProps
- **community 155** (3 nodes): LiveDot, LiveDot.tsx, LiveDotProps
- **community 156** (4 nodes): AntonMark, Logo, Logo.tsx, LogoProps
- **community 157** (3 nodes): MicIndicator, MicIndicator.tsx, MicIndicatorProps
- **community 158** (12 nodes): PrefControls.tsx, PrefInput, PrefInputProps, PrefOption, PrefSeg, PrefSegProps, PrefSelect, PrefSelectProps, PrefSlider, PrefSliderProps, PrefTog, PrefTogProps
- **community 159** (3 nodes): PrefGroup, PrefGroup.tsx, PrefGroupProps
- **community 160** (3 nodes): PrefRow, PrefRow.tsx, PrefRowProps
- **community 161** (3 nodes): ProgressBar, ProgressBar.tsx, ProgressBarProps
- **community 162** (3 nodes): RiskBars, RiskBars.tsx, RiskBarsProps
- **community 163** (4 nodes): SearchBox, SearchBox.tsx, SearchBoxProps, handle
- **community 164** (4 nodes): SegmentedControl, SegmentedControl.tsx, SegmentedControlProps, SegmentedOption
- **community 165** (3 nodes): Sparkline, Sparkline.tsx, SparklineProps
- **community 166** (3 nodes): Stat, Stat.tsx, StatProps
- **community 167** (3 nodes): Swatches, Swatches.tsx, SwatchesProps
- **community 168** (7 nodes): PersistShape, ThemeProvider, ThemeProvider.tsx, ThemeProviderProps, ThemeState, readPersisted, writePersisted
- **community 169** (4 nodes): TopBar, TopBar.tsx, TopBarNavItem, TopBarProps
- **community 170** (3 nodes): VoiceDock, VoiceDock.tsx, VoiceDockProps
- **community 171** (3 nodes): WatchRow, WatchRow.tsx, WatchRowProps
- **community 172** (3 nodes): Waveform, Waveform.tsx, WaveformProps
- **community 173** (12 nodes): Notification, Notification.tsx, Props, beginExit, cancelTtl, dismissNotification, fmtDateTime, fmtTime, notifications.icons.tsx, notify.ts, severityIcon, startTtl
- **community 174** (4 nodes): NotificationsHost, NotificationsHost.tsx, NotificationsHostProps, useNotifications
- **community 176** (8 nodes): clearNotifications, defaultTtl, emit, getServerSnapshot, getSnapshot, nextId, notifications.store.ts, pushNotification
- **community 177** (4 nodes): Notification, NotificationAction, NotificationInput, notifications.types.ts
- **community 181** (2 nodes): onSuccess, tsup.config.ts
- **community 182** (7 nodes): Probes.md, WHY_PROBES_NOT_MCP.md, broker-source-integration, cdp-chrome, enctoken, probe-cdp-not-playwright, project-cdp-prerequisite
- **community 183** (3 nodes): _probe_auth.py, _vault_secret, probe_credentials
- **community 184** (2 nodes): _run, check
- **community 186** (2 nodes): _record, run
- **community 187** (2 nodes): _check_popup_fits, _record
- **community 188** (4 nodes): afbach-vault, no-secrets-in-vcs, project-wagner-dante, vault-only-credentials
