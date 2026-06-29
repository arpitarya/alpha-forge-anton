# Probes

Probes are Python scripts in `probes/` that verify AlphaForge Anton features against a live,
running instance. They attach to the existing Chrome via CDP on port 9299 — the same session
used by broker scrapers — so there is no separate browser to manage.

See [probes/WHY_PROBES_NOT_MCP.md](../probes/WHY_PROBES_NOT_MCP.md) for why probes are preferred
over Playwright MCP.

## Prerequisites

```bash
just zerodha-chrome      # opens Chrome with CDP on :9299 (one-time per session)
just dev                 # backend :8000 + frontend :3000
```

## Running probes

```bash
just probe               # list all available probes
just probe ui            # run the UI auth/navigation probe
just probe zerodha       # run the Zerodha API probe
just probe groww-cash    # run the Groww cash probe
```

Every probe exits `0` on full pass, non-zero on any failure.

---

## Probe types

### UI probe (`ui_*_probe.py`)

Drives the frontend via Playwright. Logs in, navigates, asserts DOM state and API consistency,
saves screenshots to `screenshots/`.

**When to write one:** new page or user flow added to the frontend.

### Broker XHR probe (`<broker>_probe.py`)

Attaches to the broker's page already open in Chrome. Either:
- intercepts XHR responses (Groww, AngelOne — no public REST API), or
- reads an auth token from cookies and fires direct REST calls (Zerodha enctoken).

**When to write one:** new broker source added, or debugging live API response shapes.

### Vault check probe (`*_keys_probe.py`)

Standalone (no CDP). Reads the afbach vault over its HTTP API and asserts the
secrets a feature depends on are present and non-empty. **A probe never writes a
secret** — keys are always provisioned through bach itself
(`afbach secret set anton <KEY>`), the single source of truth. The probe is the
verification counterpart only, and never prints secret values (length only).

**When to write one:** a new feature reads an API key from the vault (e.g.
`parallel_keys_probe.py` for the signals-engine Parallel grounding key).

---

## Writing a new probe

### 1. Create the script

```
probes/<name>_probe.py          # broker probe
probes/ui_<feature>_probe.py    # UI probe
```

**Boilerplate — UI probe:**

```python
"""One-line description of what this probe verifies.

Run:
    just probe ui-<feature>
    uv run python probes/ui_<feature>_probe.py

Requires: CDP Chrome on :9299, backend :8000, frontend :3000.
Screenshots saved to <repo-root>/screenshots/.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome
from _probe_auth import probe_credentials

BASE_URL = os.getenv("AF_FRONTEND", "https://localhost:3000")
CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
USERNAME, PASSWORD = probe_credentials()
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    print(f"  {'✓' if ok else '✗'}  {label}" + (f"  {detail}" if detail else ""))


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    try:
        # navigate, assert, screenshot …
        await page.goto(f"{base}/your-page", wait_until="networkidle")
        ok = True  # replace with real assertion
        _record("Your check description", ok)
        await page.screenshot(path=str(SHOT_DIR / "yourfeature-01.png"))
    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


# ── Auth'd pages: beat the zustand-persist hydration race ──────────────────────
# A full `goto(/your-page)` runs `AuthGuard` before `zustand/persist` rehydrates the
# token, so it bounces to /login. Instead: seed storage in an INIT script (runs before
# any app script), land on `/` so the store rehydrates, then CLIENT-navigate via the
# in-app nav BUTTON (the hydrated store stays in memory across the SPA transition):
#
#   await page.add_init_script("() => { localStorage.setItem('af_token', …);"
#       " localStorage.setItem('af-auth', …); sessionStorage.setItem('af-booted','1'); }")
#   await page.goto(base, wait_until="domcontentloaded")
#   tab = page.get_by_role("button", name="Goals")   # nav label, not a <Link> href
#   await tab.first.wait_for(); await tab.first.click()
#   await page.wait_for_url("**/goals")
# See `ui_goals_probe.py` / `ui_decisions_probe.py`.


def main() -> None:
    print(f"AlphaForge Anton <Feature> Probe  →  {BASE_URL}  [CDP :{CDP_PORT}]")
    ok = asyncio.run(run(BASE_URL, CDP_PORT))
    passed = sum(1 for _, o, _ in _results if o)
    print(f"\n── Summary\n  {passed}/{len(_results)} checks passed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
```

**Boilerplate — Broker XHR probe (interception):**

```python
"""Attach to existing CDP Chrome, intercept <Broker> XHR responses.

Run:
    just probe <broker>
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

HOLDINGS_PAGE = "https://broker.example.com/holdings"
NEEDLES = ("holding", "portfolio")   # URL substrings to match


async def main() -> None:
    pw, browser = await connect_existing_chrome()
    page = await find_or_open_page(browser, HOLDINGS_PAGE, "broker.example.com")
    captured: list[dict] = []

    async def on_response(resp):  # noqa: ANN001
        if "broker.example.com" not in resp.url:
            return
        if not any(n in resp.url.lower() for n in NEEDLES):
            return
        try:
            body = await resp.json()
            captured.append({"url": resp.url, "body": body})
        except Exception:  # noqa: BLE001
            pass

    page.on("response", on_response)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)

    for item in captured:
        print(json.dumps(item, indent=2, default=str))

    await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Credentials (UI probes only)

UI probes need a Wagner username and password. `_probe_auth.probe_credentials()` resolves
them in this order:

1. `PROBE_USER` / `PROBE_PASS` environment variables
2. `afbach` vault keys `PROBE_USER` / `PROBE_PASS`
3. Error — no hardcoded fallbacks

Store credentials in the vault (preferred) or export them before running.

### 3. CDP helpers

`app.modules.brokers._cdp` exports:

| Helper | Purpose |
|---|---|
| `connect_existing_chrome(port=9299)` | Returns `(playwright, browser)` attached to the running Chrome |
| `find_or_open_page(browser, url, domain)` | Returns an existing page for the domain or opens a new one |
| `cookie_value(context, name, domain)` | Reads a cookie by name from the browser context |

### 4. Register the probe in `probe.sh`

Add the name → filename mapping in two places:

**`list_probes()`** — add a line under the right section:

```bash
    ui-<feature>         ui_<feature>_probe.py
```

**`case "$NAME" in`** — add a case:

```bash
    ui-<feature>)    SCRIPT="ui_<feature>_probe.py" ;;
```

### 5. Add a `just` recipe (optional but expected)

If this probe has a natural short alias, add a recipe to the `justfile`:

```just
# Brief description of what this probe checks
ui-<feature>:
    bash probes/probe.sh ui-<feature>
```

---

## Assertions pattern

Use `_record(label, bool, detail)` for every check. It:
- appends to `_results` so `main()` can print a summary and set the exit code
- prints `✓` / `✗` inline as the probe runs

Always take at least one screenshot per logical section so failures are visually debuggable.

## DOM anchors

UI probes should select elements by `data-af-*` attributes, not CSS class names or text.
Add the attribute to the React component if it does not exist yet:

```tsx
<button data-af-sort>Sort</button>
<div data-af-holding-row>…</div>
<input data-af-search />
```

This decouples probe selectors from styling changes.

---

## Files summary

| File | Role |
|---|---|
| `probes/probe.sh` | Dispatcher — maps probe names to scripts |
| `probes/_probe_auth.py` | Credential resolver (env → vault) |
| `probes/ui_probe.py` | Main UI auth + navigation probe |
| `probes/ui_portfolio_probe.py` | Portfolio filter / sort / search probe |
| `probes/ui_goals_probe.py` | Goals (`/goals`) on **REAL data** — loads the real mandate (`load_mandate`) + journal funnel (`library_summary`) in-process, serves them through the page's `/mandate` + `/edges/summary` fetches, and asserts the DOM: aim, Calmar 3/2, −12/−20 marks, the edge band `1 tested · 1 killed · 0 live · 100% kill-rate`, honest-pending (live Calmar "—", "not yet covered"), "Propose change" opens chat (no silent write); `just probe ui-goals` |
| `probes/ui_decisions_probe.py` | Track-U Decisions (`/decisions`) — ledger rows + calibration 13·4·3; REPLAY enabled only on replayable rows + read-only re-run summary; `just probe ui-decisions` |
| `probes/ui_flow_probe.py` | Process-flow cockpit (`/flow`) on **REAL data** — `flow_service` over the elgar journal in-process; asserts all 9 stages render for edge-001 (Test = KILL, Range→Watch BLOCKED — honest, not faked), and "New edge" opens the author panel (Family A/B/C templates, C disabled); `just probe ui-flow` |
| `probes/flow_author_probe.py` | Flow spine + Idea/Rule authoring (standalone, no CDP) — 9-node order, template availability, honest stage derivation, **server-stamped** pre-registration, pre-registration **freeze**, determinism; `just probe flow-author` |
| `probes/flow_run_probe.py` | Flow Test/Range (standalone, no CDP) — honest gate mapping (Gate-0 passed · killer FAILED · rest SKIPPED), the async job runs once per edge (no double-run), the downside-first cone. `--heavy` adds the ~30s determinism check (a UI run equals the CLI run, byte-identical signature); `just probe flow-run` |
| `probes/flow_sizing_probe.py` | Flow Plan (standalone, no CDP) — deterministic sizing: each constraint's formula (fixed-risk · downside cap · ADV cap · fractional-Kelly), the **binding minimum** is the recommendation (clamped to [0, capital]), 0-ADV drops the liquidity cap, determinism, and Plan unlocks ONLY for a surviving edge; `just probe flow-sizing` |
| `probes/flow_redteam_probe.py` | Flow Red-team — the **only LLM stage** (gateway MOCKED: no spend). Parses the model's JSON into a severity-sorted `RedteamReport`, runs one repair round on bad JSON, caches per edge (no re-bill), and asserts the module **imports no funnel/sizing engine** (off the deterministic path); `just probe flow-redteam` |
| `probes/flow_approve_probe.py` | Flow Approve (elgar write MOCKED) — the proposal is downside-first (worst-case ₹ loss leads) + carries the red-team critique, the exec checklist **never places an order**, APPROVE is refused without ack-loss, VETO needs a reason, a **PAN in the veto reason is BLOCKED before elgar**, and a clean decision stamps a cooldown; `just probe flow-approve` |
| `probes/flow_live_probe.py` | Flow Live — the **NEVER-auto-execute** invariant. The order plan is copy-only (entry + staged −12/−20 guard) and says Orff never places an order; reconciliation computes true P&L + slippage vs the plan and lights the guard at −12/−20; and the Live engine **imports no broker module and makes no order-placement call**; `just probe flow-live` |
| `probes/flow_watch_probe.py` | Flow Watch (elgar write MOCKED) — deterministic decay: a healthy series stays healthy; a decayed one (negative expectancy / −20% drawdown / losing streak) recommends a decay-kill with severity-tagged signals; the decay-kill **PII-guards its reason** and the engine **imports no broker / edge_store** (the frozen spec is never mutated); `just probe flow-watch` |
| `probes/ui_proposal_probe.py` | Track-U inline Orff proposal (`/proposal` demo) — pinned guardrail strip; cone red worst-case; calibration chip (13 cleared); Approve gated until the ES loss is tapped; `just probe ui-proposal` |
| `probes/ui_feedstate_probe.py` | Track-U feed liveness — STALE freezes the cone to ₹0 ("not because you're flat") + blocks Approve even after ack; LIVE restores both; `just probe ui-feedstate` |
| `probes/<broker>_probe.py` | Broker-specific XHR / REST probes |
| `probes/pypi_publish_probe.py` | Release health — fux-engine / cage-flux are live on PyPI |
| `probes/github_publish_probe.py` | Release health — the fux/cage publish & CI workflows are green |
| `probes/plan_safety_probe.py` | Constitutional guard — money docs / hard PII never tracked in the repo (commit boundary); `just probe plan-safety` |
| `probes/critic_runtime_probe.py` | Runtime money/PII guard — a forbidden note (PAN/Aadhaar/account) is refused at `append_memory` before the elgar write; `just probe critic-runtime` (the live-write twin of `plan-safety`) |
| `probes/parallel_keys_probe.py` | Vault check — Parallel (parallel.ai) API key is provisioned in afbach |
| `probes/deep_search_probe.py` | §9 agent-initiated deep search — auto card (no call) / confirm (call+receipt) / reject / always (cardless) / never / over-budget degrade |
| `probes/ui_deep_search_probe.py` | §9 frontend (CDP, fixture-served) — tri-state Auto/Always/Never control renders + sends `deep_search_mode`, persists the pref; an Auto gap raises the request_deep_search card (reasons + queries + cost) and Approve dispatches the run |
| `probes/ui_deep_search_close_probe.py` | §9 regression guard (CDP, fixture-served) — approving the deep-search card **closes the loop in one turn**: Approve awaits `/deep-search`, resends a single follow-up carrying the `{grounding}` with `deep_search_mode="never"`, the reconciliation answer renders, and the card does **not** re-arm; `just probe ui-deep-search-close` / `just deep-search-close` |
| `probes/signals_review_probe.py` | Signals Phase 1 — deterministic ActionPlan (byte-identical) on a fixture; `just signals-review` |
| `probes/signals_screen_probe.py` | Signals Phase 2 — deterministic ScreenResult (ranking + gates) on a fixture universe; `just probe signals-screen` |
| `probes/signals_replan_probe.py` | Signals Phase 3 — re-plan loop reports the diff (exited/new/stops/un-acted) on changed holdings; `just probe signals-replan` |
| `probes/signals_pnl_probe.py` | Signals Phase 4 — monthly tracker nets brokerage/STT/friction/STCG on a fixture; `just probe signals-pnl` |
