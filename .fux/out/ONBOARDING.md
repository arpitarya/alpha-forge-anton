# Onboarding — a generated reading path

_Read top to bottom. Each entry: `fux why <id>` for the full text._


## narrative
1. **architecture** — AlphaForge Anton — Architecture & Key Files
2. **broker-csv-dumps** — Broker CSV Dump Convention
3. **broker-source-integration** — Broker Source Integration Guide
4. **commands** — AlphaForge Anton — Commands
5. **getting-started** — Getting Started — Developer Setup
6. **how** — How AlphaForge Anton Works
7. **live-prices-plan** — Live prices — design plan
8. **plan-boot-llm-brokerage** — Plan: Add LLM + Brokerage Sync to Boot Screen
9. **what** — What AlphaForge Anton Is
10. **why** — Why AlphaForge Anton Exists
11. **anton-overview** — Why Anton exists

## convention
12. **async-everywhere** — In async services, I/O-bound code is `async` end-to-end — no
13. **files-max-100-lines** — Source files stay ≤ 100 lines (≤ 50 for files whose name
14. **doc-per-code-change** — Every code change ships with the knowledge update it implies in
15. **no-secrets-in-vcs** — Never commit secrets — `.env` files, API keys, tokens, private

## rule
16. **inr-normalization** — Every holding's monetary fields are converted to INR via `to_inr(value,

## formula
17. **day-pnl** — Today's P&L is computed on current INR value, not invested cost:
18. **portfolio-valuation** — Portfolio totals are computed over INR-normalised holdings:

## invariant
19. **holdings-sum-equals-total** — The portfolio's `current_value` total must equal the sum of

## regulatory
20. **market-hours-nse** — NSE/BSE equity continuous trading runs 09:15–15:30 IST
21. **capital-gains-equity** — For listed Indian equity / equity mutual funds, the holding

## memory
22. **project-broker-prime** — `backend/app/modules/brokers/refetch.py` runs a one-shot `_prime_unsynced` ta…
23. **project-fux** — Fux is a new sibling tool (beside wagner/bach/orff), implemented 2026-06-02 at
24. **project-wagner-dante** — Wagner IAM and Dante security have been fully integrated as of 2026-05-25.
