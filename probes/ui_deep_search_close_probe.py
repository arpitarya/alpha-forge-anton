"""Playwright CDP probe — the deep-search confirm→apply loop now CLOSES in one turn.

Regression guard for the bug where approving a "Deep web search" card discarded the
{grounding} response and resent the turn still in deep_search_mode="auto", so the card
re-armed forever (elgar://session/kreglqek). Attaches to the existing Chrome CDP session
(:9299), injects a dev JWT, and fixture-serves the concierge SSE + /deep-search endpoint
(hermetic in data, real in render — honouring the probes-not-MCP rule). Asserts only what
the browser renders + sends:

  1. Reaching the app (not redirected to /login)
  2. An Auto-mode fresh-data turn raises the request_deep_search confirm card
  3. Approving the card AWAITS /deep-search and resends ONE follow-up that carries the
     returned {grounding} AND deep_search_mode="never" (so Orff answers, never re-asks)
  4. The reconciliation answer renders
  5. NO second deep-search card appears — the gate did not re-arm

Run:
    uv run python probes/ui_deep_search_close_probe.py
    just probe ui-deep-search-close

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
GROUNDING = "PARAS bagged a ₹500 Cr defence order on 2026-06-18 (https://x.test)."

_results: list[tuple[str, bool, str]] = []

FAKE_USER = {
    "guid": "00000000-0000-0000-0000-000000000001",
    "email": "probe@local.dev",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
}

DEEP_SEARCH_CARD = {"confirm": {
    "id": "deep-search",
    "action": "Deep web search",
    "summary": "Need live PARAS defence-order news past my knowledge cutoff",
    "steps": ["PARAS defence order 2026"],
    "detail": "~₹0.5 · ₹3 of ₹500 used this month",
    "apply": {"path": "/api/v1/concierge/deep-search",
              "body": {"queries": ["PARAS defence order 2026"]}},
}}
_META = {"provider": "claude-sdk", "model": "claude-opus-4-8", "elapsed_s": 0.1}
CARD_DONE = {"content": "Action proposed — please confirm.", **_META}
ANSWER_DONE = {"content": "PARAS won a ₹500 Cr order on 2026-06-18 — reconciled.", **_META}

# Mutable spy — what the fixture observed across requests.
_seen: dict = {"cards": 0, "grounded_mode": None, "grounded": False, "dispatched": False}


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
    """A turn carrying `grounding` is the post-approval closing turn → plain answer, no
    card. A fresh-data ("PARAS") turn without grounding raises the card (counted)."""
    body = route.request.post_data or ""
    try:
        data = json.loads(body)
    except Exception:
        data = {}
    if data.get("grounding"):  # the closing turn — must NOT re-arm
        _seen["grounded"] = True
        _seen["grounded_mode"] = data.get("deep_search_mode")
        await route.fulfill(status=200, content_type="text/event-stream", body=_sse(ANSWER_DONE))
        return
    if "PARAS" in body:
        _seen["cards"] += 1
        await route.fulfill(status=200, content_type="text/event-stream",
                            body=_sse(DEEP_SEARCH_CARD, CARD_DONE))
        return
    await route.fulfill(status=200, content_type="text/event-stream",
                        body=_sse({"content": "ok", **_META}))


async def _deep_search_route(route) -> None:
    """The card's apply target — Approve must AWAIT this and feed back {grounding}."""
    _seen["dispatched"] = True
    await route.fulfill(status=200, content_type="application/json",
                        body=json.dumps({"grounding": GROUNDING}))


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
    await page.get_by_role("tab", name="Chat mode").click()
    await page.wait_for_timeout(300)
    footer = page.locator("#chatinput-bar")
    await footer.wait_for(state="visible", timeout=5_000)
    await footer.fill("Hello")
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
        if not await _open_rail(page):
            return False

        print("\n── Auto gap → request_deep_search confirm card")
        await _send_in_rail(page, "What's the latest on PARAS defence orders?")
        await page.wait_for_selector("text=confirm to proceed", timeout=6_000)
        await page.wait_for_timeout(200)
        _record("Auto turn raised exactly one card", _seen["cards"] == 1, str(_seen["cards"]))
        await page.screenshot(path=str(SHOT_DIR / "dsclose-01-card.png"))

        print("\n── Approve closes the loop in one turn")
        await page.get_by_role("button", name="Approve & continue").click()
        # Wait for the closing turn's reconciliation answer (proves grounding was consumed).
        await page.wait_for_function(
            """() => document.body.innerText.includes('reconciled')""", timeout=8_000)
        await page.wait_for_timeout(400)
        _record("Approve awaited /deep-search (dispatched)", _seen["dispatched"])
        _record("Closing turn carried the grounding", _seen["grounded"])
        _record("Closing turn forced deep_search_mode=never",
                _seen["grounded_mode"] == "never", str(_seen["grounded_mode"]))
        _record("Reconciliation answer rendered",
                "reconciled" in (await page.evaluate("() => document.body.innerText")))
        _record("Card did NOT re-arm (still exactly one card seen)",
                _seen["cards"] == 1, str(_seen["cards"]))
        await page.screenshot(path=str(SHOT_DIR / "dsclose-02-answer.png"))

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

    print(f"Deep-search Close-Loop UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
