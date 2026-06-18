"""Playwright CDP probe — the tri-state Deep-search control + request_deep_search card.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT, and
fixture-serves the concierge SSE (hermetic in data, real in render — honouring the
probes-not-MCP rule). Phase-2 frontend of docs/handoffs/deep-search-ask.handoff.md.
Asserts only what the browser renders + sends:

  1. Reaching the app (not redirected to /login)
  2. The composer shows a tri-state control (Auto / Always / Never), Auto default
  3. The default request carries deep_search_mode="auto"
  4. Picking "Always" persists the pref and sends deep_search_mode="always"
  5. An Auto-mode fresh-data turn raises the request_deep_search confirm card showing
     the reasons (summary), the queries (steps), and the cost/budget line (detail)
  6. Approving the card dispatches POST /api/v1/concierge/deep-search

Run:
    uv run python probes/ui_deep_search_probe.py
    just probe ui-deep-search

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

# The request_deep_search confirm card (deep_search_service.confirm_card shape). Figures
# are the handoff's own example values, not a real target (the real ₹ lives only in elgar).
DEEP_SEARCH_CARD = {"confirm": {
    "id": "deep-search",
    "action": "Deep web search",
    "summary": "Need live PARAS defence-order news past my knowledge cutoff",
    "steps": ["PARAS defence order 2026", "PARAS Q2 FY26 results"],
    "detail": "~₹0.5 · ₹3 of ₹500 used this month",
    "apply": {"path": "/api/v1/concierge/deep-search",
              "body": {"queries": ["PARAS defence order 2026", "PARAS Q2 FY26 results"]}},
}}
_META = {"provider": "claude-sdk", "model": "claude-opus-4-8", "elapsed_s": 0.1}
CARD_DONE = {"content": "Action proposed — please confirm.", **_META}
PLAIN_DONE = {"content": "Here is your answer from the free sources.", **_META}

# Mutable spy — what the fixture observed across requests.
_seen: dict = {"last_mode": None, "dispatched": False}


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
    """Record the request's deep_search_mode; a fresh-data ("PARAS") query that is not
    itself the post-confirm follow-up raises the deep-search card, else a plain reply."""
    body = route.request.post_data or ""
    try:
        _seen["last_mode"] = json.loads(body).get("deep_search_mode")
    except Exception:
        _seen["last_mode"] = None
    gap = "PARAS" in body and "Yes — proceed" not in body
    sse = _sse(DEEP_SEARCH_CARD, CARD_DONE) if gap else _sse(PLAIN_DONE)
    await route.fulfill(status=200, content_type="text/event-stream", body=sse)


async def _deep_search_route(route) -> None:
    """The card's apply target — confirming the card must POST here."""
    _seen["dispatched"] = True
    await route.fulfill(status=200, content_type="application/json",
                        body=json.dumps({"grounding": "PARAS order win (https://x.test)"}))


async def _inject_auth_and_navigate(page, base: str, token: str) -> bool:
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({"state": {"accessToken": token, "refreshToken": None,
                                       "user": FAKE_USER}, "version": 0})
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.removeItem('af_refresh_token');
        localStorage.removeItem('af-model-choice');
        localStorage.removeItem('af-deep-search-mode');
        localStorage.setItem('af-mode', 'chat');
        sessionStorage.setItem('af-booted', '1');
    }}""")
    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


async def _open_rail(page) -> bool:
    """Seed a query (footer bar) to open the rail — hits the plain-reply branch."""
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
        await page.wait_for_timeout(500)
        return True
    except Exception as e:
        _record("Chat rail open", False, str(e))
        return False


async def _send_in_rail(page, text: str) -> None:
    ta = page.locator("#chatinput")
    await ta.fill(text)
    await ta.press("Enter")
    await page.wait_for_timeout(700)


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
    await page.route("**/api/v1/concierge", _concierge_route)
    await page.route("**/api/v1/concierge/deep-search", _deep_search_route)

    try:
        print("\n── Auth + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached app (not /login)", on_app, page.url)
        if not on_app:
            return False
        await page.wait_for_selector('[aria-haspopup="dialog"]', timeout=15_000)

        print("\n── Open rail (seed carries the default mode)")
        if not await _open_rail(page):
            return False
        _record("Chat rail opened", True)
        _record("Default request sends deep_search_mode=auto", _seen["last_mode"] == "auto",
                str(_seen["last_mode"]))

        print("\n── Tri-state control renders")
        group = page.locator("[data-af-deep-search]")
        await group.wait_for(state="visible", timeout=5_000)
        seg_ids = await page.evaluate(
            """() => [...document.querySelectorAll('[data-af-deep-search] [data-mode]')]"""
            """.map(b => b.getAttribute('data-mode'))""")
        _record("Three segments render (auto/always/never)",
                seg_ids == ["auto", "always", "never"], str(seg_ids))
        auto_pressed = await page.locator('[data-mode="auto"]').get_attribute("aria-pressed")
        _record("Auto is the active default", auto_pressed == "true", str(auto_pressed))
        await page.screenshot(path=str(SHOT_DIR / "ds-01-control.png"))

        print("\n── Pick Always → persists + sends the mode")
        await page.locator('[data-mode="always"]').click()
        await page.wait_for_timeout(150)
        always_pressed = await page.locator('[data-mode="always"]').get_attribute("aria-pressed")
        stored = await page.evaluate("() => localStorage.getItem('af-deep-search-mode')")
        _record("Always becomes active", always_pressed == "true", str(always_pressed))
        _record("Choice persisted to localStorage", stored == "always", str(stored))
        await _send_in_rail(page, "Scan midcap IT breakouts")
        _record("Request sends deep_search_mode=always", _seen["last_mode"] == "always",
                str(_seen["last_mode"]))

        print("\n── Auto gap → request_deep_search confirm card")
        await page.locator('[data-mode="auto"]').click()
        await page.wait_for_timeout(150)
        await _send_in_rail(page, "What's the latest on PARAS defence orders?")
        await page.wait_for_selector("text=confirm to proceed", timeout=6_000)
        await page.wait_for_timeout(200)
        txt = await page.evaluate("() => document.body.innerText")
        _record("Auto turn raised the deep-search card", "Deep web search" in txt)
        _record("Card shows the reasons (summary)",
                "Need live PARAS defence-order news" in txt)
        _record("Card shows the queries (steps)", "PARAS defence order 2026" in txt)
        _record("Card shows the cost/budget line (detail)",
                "~₹0.5" in txt and "of ₹500" in txt)
        await page.screenshot(path=str(SHOT_DIR / "ds-02-card.png"))

        print("\n── Approve dispatches the run")
        _seen["dispatched"] = False
        await page.get_by_role("button", name="Approve & continue").click()
        await page.wait_for_timeout(700)
        _record("Approve POSTs /api/v1/concierge/deep-search", _seen["dispatched"])
        await page.screenshot(path=str(SHOT_DIR / "ds-03-dispatched.png"))

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

    print(f"Deep-search UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
