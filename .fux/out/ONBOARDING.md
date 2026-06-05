# Onboarding — a generated reading path

_Read top to bottom. Each entry: `fux why <id>` for the full text._


## narrative
1. **anton-overview** — Why Anton exists

## convention
2. **async-everywhere** — In async services, I/O-bound code is `async` end-to-end — no
3. **files-max-100-lines** — Source files stay ≤ 100 lines (≤ 50 for files whose name
4. **doc-per-code-change** — Every code change ships with the knowledge update it implies in
5. **no-secrets-in-vcs** — Never commit secrets — `.env` files, API keys, tokens, private

## rule
6. **inr-normalization** — Every holding's monetary fields are converted to INR via `to_inr(value,

## formula
7. **day-pnl** — Today's P&L is computed on current INR value, not invested cost:
8. **portfolio-valuation** — Portfolio totals are computed over INR-normalised holdings:

## invariant
9. **holdings-sum-equals-total** — The portfolio's `current_value` total must equal the sum of

## regulatory
10. **market-hours-nse** — NSE/BSE equity continuous trading runs 09:15–15:30 IST
11. **capital-gains-equity** — For listed Indian equity / equity mutual funds, the holding

## memory
12. **project-broker-prime** — `backend/app/modules/brokers/refetch.py` runs a one-shot `_prime_unsynced` ta…
13. **project-fux** — Fux is a new sibling tool (beside wagner/bach/orff), implemented 2026-06-02 at
14. **project-wagner-dante** — Wagner IAM and Dante security have been fully integrated as of 2026-05-25.
