"""CDP probe — feed liveness gating in the inline proposal (LIVE/STALE).

Attaches to the existing Chrome CDP session (:9299), injects a dev JWT, opens the
`/proposal` demo (MOCK — no API), and asserts the honest-pending feed contract:

  1. STALE freezes the cone to ₹0 — "not because you're flat", it won't re-price
  2. STALE blocks Approve (even after the loss is acknowledged)
  3. LIVE restores the cone (worst-case re-prices) and lets Approve unlock

Run:  uv run python probes/ui_feedstate_probe.py   |   just probe ui-feedstate
Screenshots → <repo-root>/screenshots/.
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
_META = {"provider": "claude-sdk", "model": "claude-opus-4-8", "elapsed_s": 0.1}
PLAIN_DONE = {"content": "Ready.", **_META}


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


async def _setup(page) -> None:
    await page.route("**/api/v1/iam/me", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(FAKE_USER)))
    await page.route("**/api/v1/health/boot/sync-stream", lambda r: r.fulfill(
        status=200, content_type="text/event-stream", body=""))
    await page.route("**/api/v1/health/boot", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"services": [
            {"key": "backend", "label": "Backend", "status": "ok", "detail": "online"}]})))
    await page.route("**/api/v1/concierge", lambda r: r.fulfill(
        status=200, content_type="text/event-stream", body=_sse(PLAIN_DONE)))


async def _navigate(page, base: str, token: str) -> bool:
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({"state": {"accessToken": token, "refreshToken": None,
                                       "user": FAKE_USER}, "version": 0})
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.setItem('af-mode', 'chat');
        sessionStorage.setItem('af-booted', '1');
    }}""")
    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


async def open_proposal_demo(page) -> None:
    await page.get_by_role("tab", name="Chat mode").click()
    await page.wait_for_timeout(300)
    footer = page.locator("#chatinput-bar")
    await footer.wait_for(state="visible", timeout=5_000)
    await footer.fill("Hello")
    await footer.press("Enter")
    await page.wait_for_function("""() => {
        const a = document.querySelector('[aria-label="Alpha chat"]');
        return a && getComputedStyle(a).pointerEvents !== 'none';
    }""", timeout=6_000)
    composer = page.locator("#chatinput")
    await composer.fill("/proposal")
    await composer.press("Enter")
    await page.wait_for_selector("[data-proposal-demo]", timeout=6_000)
    await page.wait_for_timeout(300)


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()
    await _setup(page)

    try:
        print("\n── Auth + navigation")
        if not await _navigate(page, base, token):
            _record("Reached app (not /login)", False, page.url)
            return False
        _record("Reached app (not /login)", True, page.url)
        await page.wait_for_selector('[aria-haspopup="dialog"]', timeout=15_000)
        await open_proposal_demo(page)

        print("\n── STALE freezes the cone + blocks approval")
        await page.locator('[data-feed="stale"]').click()
        await page.wait_for_timeout(300)
        body = await page.evaluate("() => document.body.innerText")
        _record("Cone refuses to re-price (₹0 — not because you're flat)",
                "not because you're flat" in body and "won't re-price" in body)
        _record("Approve blocked on stale feed",
                "feed stale — approval blocked" in body
                and await page.get_by_role("button", name="Approve — acknowledge loss first").first.is_disabled())
        # Even acknowledging the loss must not unlock Approve while stale.
        await page.locator(".of-loss .ack").first.click()
        await page.wait_for_timeout(200)
        still_locked = await page.get_by_role(
            "button", name="Approve — acknowledge loss first").first.is_disabled()
        _record("Ack does NOT unlock Approve while stale", still_locked)
        await page.screenshot(path=str(SHOT_DIR / "feedstate-01-stale.png"))

        print("\n── LIVE restores the cone + lets Approve unlock")
        await page.locator('[data-feed="live"]').click()
        await page.wait_for_timeout(300)
        body2 = await page.evaluate("() => document.body.innerText")
        _record("Cone re-prices on live feed (worst −₹1.4L)", "−₹1.4L" in body2)
        unlocked = page.get_by_role("button", name="Approve as proposed →")
        _record("Approve unlockable on live feed",
                await unlocked.count() >= 1 and await unlocked.first.is_enabled())
        await page.screenshot(path=str(SHOT_DIR / "feedstate-02-live.png"))

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

    print(f"FeedState UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
