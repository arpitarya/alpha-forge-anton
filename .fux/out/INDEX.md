# Fux INDEX

_50 active entries across 11 domains. Read this first; open a rule (`fux why <id>`) only when relevant._

## architecture
- **mutation-confirm-rmw** (rule) — every Orff-initiated mutation (memory note, exclusion-list edit, strategy/obj…

## brokers
- **broker-source** (glossary) — BrokerSource
- **broker-source-contract** (convention) — Every holdings provider is a `BrokerSource` subclass
- **cdp-chrome** (glossary) — CDP Chrome (port 9299)
- **dump-utils-single-source** (convention) — All broker CSV I/O goes through
- **enctoken** (glossary) — enctoken
- **holding** (glossary) — Holding
- **probe-cdp-not-playwright** (convention) — UI and broker verification is done with scripts in `probes/` that
- **source-kind-status** (glossary) — SourceKind / SourceStatus

## code-quality
- **async-everywhere** (convention) — In async services, I/O-bound code is `async` end-to-end — no _[global]_
- **files-max-100-lines** (convention) — Source files stay ≤ 100 lines (≤ 50 for files whose name _[global]_

## concierge
- **concierge-default-model** (convention) — A fresh Orff session pins a derived default model, never the
- **concierge-registry-single-source** (convention) — The concierge provider/model registry, intent→provider routing,
- **orff** (glossary) — Orff
- **projection-disclosure** (convention) — every forward projection Orff presents must satisfy four

## frontend
- **ui-component-contract** (convention) — A UI Orff generates on the fly is a declarative UISpec — a JSON

## market-structure
- **market-hours-nse** (regulatory) — NSE/BSE equity continuous trading runs 09:15–15:30 IST
- **transaction-costs** (regulatory) — Every Indian equity round-trip pays a stack of frictions

## portfolio
- **capital-market-assumptions** (rule) — Capital-market assumptions — expected returns used for projections
- **core-allocation** (glossary) — core-allocation
- **day-pnl** (formula) — Today's P&L is computed on current INR value, not invested cost:
- **drawdown-recovery** (formula) — the gain required to recover a drawdown is convex in the loss:
- **emergency-fund-first** (rule) — an emergency buffer of 6 months of expenses (12 if income is
- **holdings-aggregator** (glossary) — HoldingsAggregator
- **holdings-sum-equals-total** (invariant) — The portfolio's `current_value` total must equal the sum of
- **inr-normalization** (rule) — Every holding's monetary fields are converted to INR via `to_inr(value,
- **portfolio-plan-template** (glossary) — portfolio-plan-template
- **portfolio-valuation** (formula) — Portfolio totals are computed over INR-normalised holdings:
- **position-concentration** (rule) — Default concentration ceilings Orff applies when reviewing holdings
- **rebalancing-policy** (rule) — Rebalancing is band-triggered, not calendar-triggered, and follows
- **signals-deterministic-core** (rule) — the signals engine is a deterministic core with a probabilistic edge.
- **strategy-knob-tradeoffs** (rule) — the signals engine's behaviour is governed by a small set of tunable
- **xirr-vs-cagr** (formula) — Use the return measure that matches the cash-flow shape:

## process
- **doc-per-code-change** (convention) — Every code change ships with the knowledge update it implies in _[global]_
- **finance-feature-playbook** (convention) — a new financial metric/insight ships through a fixed seven-step

## project
- **project-broker-prime** (memory) — `backend/app/modules/brokers/refetch.py` exposes `prime_in_background`, which…
- **project-cdp-prerequisite** (memory) — Every API-kind broker sync (and every probe) depends on an externally launched
- **project-fux** (memory) — Fux is a sibling tool (beside wagner/bach/orff) at `~/my_programs/fux` (remote
- **project-wagner-dante** (memory) — Wagner IAM and Dante security have been fully integrated as of 2026-05-25.

## security
- **afbach-vault** (glossary) — afbach vault (alpha-forge-bach)
- **context-docs-figure-free** (rule) — Orff's standing-context / memory docs hold durable preferences and rules only…
- **knowledge-location** (convention) — every authored knowledge document lives in exactly one of two
- **no-secrets-in-vcs** (convention) — Never commit secrets — `.env` files, API keys, tokens, private _[global]_
- **plan-store** (convention) — Plan store (elgar) — money documents are linked, never stored
- **trusted-lane-tools** (rule) — Orff's tool-calling and paid web grounding are governed by the trusted lane.
- **vault-only-credentials** (convention) — Broker credentials — user IDs, client IDs, API keys — live only

## tax
- **capital-gains-debt-gold** (regulatory) — Non-equity assets follow different holding-period and rate
- **capital-gains-equity** (regulatory) — For listed Indian equity / equity mutual funds, the holding
- **crypto-tax-vda** (regulatory) — Crypto and other Virtual Digital Assets (VDAs) have their
- **tax-loss-harvesting** (regulatory) — Capital losses offset capital gains under fixed asymmetric
