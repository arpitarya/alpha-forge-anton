"""Playwright CDP probe — the Objective (north-star) tab in the Orff chat popup.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT, and
feeds GET /signals/objective a deterministic fixture: hermetic in data (no live
broker/elgar dependency, not flaky) but real in render (CDP Chrome, honouring the
probes-not-MCP rule). The progress_pct *maths* is a separate pure layer covered by
`objective_probe.py` — this probe asserts only what the browser renders:

  1. Reaching the app (not redirected to /login)
  2. Opening the chat rail
  3. Objective tab renders the target (active_target + step_up note + mission)
  4. Progress is a DISTINCT pending state — not a misleading 0%-width bar
  5. Proposing an edit raises an ApprovalCard (confirm card) in the thread —
     routed through set_objective, never a silent write

Run:
    uv run python probes/ui_objective_probe.py
    just probe ui-objective

Screenshots saved to <repo-root>/screenshots/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import warnings
from pathlib import Path

import jwt as pyjwt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome

DEFAULT_BASE = "https://localhost:3000"
DEFAULT_CDP = 9299
JWT_SECRET = "dev-secret-change-me"
JWT_ALGO = "HS256"
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

_results: list[tuple[str, bool, str]] = []

FAKE_USER = {
    "guid": "00000000-0000-0000-0000-000000000001",
    "email": "probe@local.dev",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
}

# Deterministic fixture — figure-free in the repo sense (these are the handoff's own
# example values, not a real personal target; the real ₹ lives only in elgar).
OBJECTIVE_FIXTURE = {
    "monthly_target_inr": 2000,
    "step_up": {"from_date": "2026-07-01", "monthly_target_inr": 12000},
    "horizon": "swing",
    "risk_tolerance": "aggressive",
    "mission": "Fund the Claude Max plan from swing profits",
    "active_target": 2000,
    "generated_at": "2026-06-15T00:00:00Z",
}

# The confirm card set_objective emits (tool_executor.build_confirm shape).
CONFIRM_EVENT = {"confirm": {
    "id": "set-objective",
    "action": "Update objective (monthly_target_inr=5000)",
    "summary": "Write new north-star target to elgar strategy/objective.md.",
    "steps": ["Validate Objective schema", "Merge into elgar strategy/objective.md", "Commit"],
    "apply": {"path": "/api/v1/signals/objective", "body": {"monthly_target_inr": 5000}},
}}
_META = {"provider": "claude-sdk", "model": "claude-opus-4-8", "elapsed_s": 0.1}
CONFIRM_DONE = {"content": "Action proposed — please confirm.", **_META}
PLAIN_DONE = {"content": "Your portfolio summary is above.", **_META}


def _sse(*events: dict) -> str:
    return "".join(f"data: {json.dumps(e)}\n\n" for e in events) + "data: [DONE]\n\n"


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    print(f"  {'✓' if ok else '✗'}  {label}" + (f"  [{detail}]" if detail else ""))


def _mint_token() -> str:
    now = int(time.time())
    payload = {"sub": FAKE_USER["guid"], "role": FAKE_USER["role"],
               "email": FAKE_USER["email"], "iat": now, "exp": now + 3600}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def _concierge_route(route) -> None:
    """An edit prompt (carries the objective target) → confirm SSE; anything else
    (the rail-opening seed) → a plain text reply. Lets us prove the *edit* raised it."""
    body = route.request.post_data or ""
    sse = _sse(CONFIRM_EVENT, CONFIRM_DONE) if "realized-profit target" in body else _sse(PLAIN_DONE)
    await route.fulfill(status=200, content_type="text/event-stream", body=sse)


async def _inject_auth_and_navigate(page, base: str, token: str) -> bool:
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({"state": {"accessToken": token, "refreshToken": None,
                                       "user": FAKE_USER}, "version": 0})
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.removeItem('af_refresh_token');
        localStorage.removeItem('af-model-choice');
        localStorage.setItem('af-mode', 'chat');
        sessionStorage.setItem('af-booted', '1');
    }}""")
    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


async def _open_rail(page) -> bool:
    """Seed a query to open the rail (the seed hits the plain-reply branch)."""
    await page.get_by_role("tab", name="Chat mode").click()
    await page.wait_for_timeout(300)
    footer = page.locator("#chatinput-bar")
    await footer.wait_for(state="visible", timeout=5_000)
    await footer.fill("What is my portfolio worth?")
    await footer.press("Enter")
    try:
        await page.wait_for_function("""() => {
            const a = document.querySelector('[aria-label="Alpha chat"]');
            return a && getComputedStyle(a).pointerEvents !== 'none';
        }""", timeout=6_000)
        await page.wait_for_timeout(400)
        return True
    except Exception as e:
        _record("Chat rail open", False, str(e))
        return False


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    await page.route("**/api/v1/iam/me", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(FAKE_USER)))
    await page.route("**/api/v1/health/boot/sync-stream", lambda r: r.fulfill(
        status=200, content_type="text/event-stream", body=""))
    await page.route("**/api/v1/health/boot", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"services": [
            {"key": "backend", "label": "Backend", "status": "ok", "detail": "online"},
            {"key": "llm", "label": "AI Gateway", "status": "ok", "detail": "ready"}]})))
    # Hermetic objective data — deterministic target, no live elgar/broker read.
    await page.route("**/api/v1/signals/objective", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(OBJECTIVE_FIXTURE)))
    await page.route("**/api/v1/concierge", _concierge_route)

    try:
        print("\n── Auth + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached app (not /login)", on_app, page.url)
        if not on_app:
            return False
        await page.wait_for_selector('[aria-haspopup="dialog"]', timeout=15_000)

        print("\n── Open rail")
        rail = await _open_rail(page)
        _record("Chat rail opened", rail)
        if not rail:
            return False

        print("\n── Objective tab")
        await page.locator('button[title="Objective"]').click()
        await page.wait_for_function("""() => {
            const el = document.body.innerText;
            return el.includes('Monthly target') && el.includes('2,000');
        }""", timeout=6_000)
        # Panel === objective unmounts the thread, so body text is the panel's content.
        panel = await page.evaluate("() => document.body.innerText")
        _record("Objective tab renders the target (₹2,000/mo)", "2,000" in panel and "/mo" in panel)
        _record("Step-up note renders (→ ₹12,000 from 2026-07-01)",
                "12,000" in panel and "2026-07-01" in panel)
        _record("Mission renders", "Fund the Claude Max plan" in panel)
        await page.screenshot(path=str(SHOT_DIR / "obj-01-tab.png"))

        # Progress is a DISTINCT pending state, not a 0%-width fill.
        pending_visible = await page.locator('[data-progress="pending"]').is_visible()
        _record("Progress is a distinct pending state (not a 0% bar)",
                pending_visible and "pending" in panel.lower()
                and "No trades source connected" in panel)

        print("\n── Edit raises a confirm card (never a silent write)")
        await page.get_by_placeholder("New monthly target ₹").fill("5000")
        await page.get_by_role("button", name="Propose change").click()
        # Panel closes → thread shows; the edit POST hits the confirm branch.
        await page.wait_for_selector("text=confirm to proceed", timeout=6_000)
        cards = page.get_by_text("confirm to proceed")
        raised = await cards.count() >= 1
        action_txt = await page.get_by_text("Update objective").first.is_visible()
        _record("Proposing an edit raises an ApprovalCard", raised and action_txt)
        # The seed reply was plain text → the card can only be from the edit.
        _record("Card carries the set_objective action", action_txt)
        await page.screenshot(path=str(SHOT_DIR / "obj-02-confirm.png"))

    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--cdp-port", type=int, default=DEFAULT_CDP)
    args = parser.parse_args()

    print(f"Objective UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
