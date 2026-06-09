# Fux INDEX

_14 active entries across 8 domains. Read this first; open a rule (`fux why <id>`) only when relevant._

## code-quality
- **async-everywhere** (convention) — In async services, I/O-bound code is `async` end-to-end — no _[global]_
- **files-max-100-lines** (convention) — Source files stay ≤ 100 lines (≤ 50 for files whose name _[global]_

## frontend
- **ui-component-contract** (convention) — A UI Orff generates on the fly is a declarative UISpec — a JSON

## market-structure
- **market-hours-nse** (regulatory) — NSE/BSE equity continuous trading runs 09:15–15:30 IST _[pack:indian-markets-tax]_

## portfolio
- **day-pnl** (formula) — Today's P&L is computed on current INR value, not invested cost:
- **holdings-sum-equals-total** (invariant) — The portfolio's `current_value` total must equal the sum of
- **inr-normalization** (rule) — Every holding's monetary fields are converted to INR via `to_inr(value,
- **portfolio-valuation** (formula) — Portfolio totals are computed over INR-normalised holdings:

## process
- **doc-per-code-change** (convention) — Every code change ships with the knowledge update it implies in _[global]_

## project
- **project-broker-prime** (memory) — `backend/app/modules/brokers/refetch.py` runs a one-shot `_prime_unsynced` ta…
- **project-fux** (memory) — Fux is a sibling tool (beside wagner/bach/orff) at `~/my_programs/fux` (remote
- **project-wagner-dante** (memory) — Wagner IAM and Dante security have been fully integrated as of 2026-05-25.

## security
- **no-secrets-in-vcs** (convention) — Never commit secrets — `.env` files, API keys, tokens, private _[global]_

## tax
- **capital-gains-equity** (regulatory) — For listed Indian equity / equity mutual funds, the holding _[pack:indian-markets-tax]_
