"""CDP probe — the Goals surface (editable north-star) at /goals.

Attaches to the existing Chrome CDP session (:9299), injects a dev JWT, and asserts
what the browser renders on Track-U MOCK data (no live broker/elgar/API dependency):

  1. Reaching /goals (not redirected to /login)
  2. Calmar hero renders (2.4×) with target 3.0 / floor 2.0
  3. Drawdown-guard meter shows the −12% soft and −20% hard marks
  4. Edges / reserve / structure render DASHED PENDING — never a faked 0% bar;
     self-funding says "not yet covered"
  5. The first-run toggle flips Calmar to a pending "—" (honest-absence)
  6. "Propose change →" opens chat and routes a prompt (never a silent write —
     the page has no PUT; the edit becomes a confirm card in the rail)

Run:  uv run python probes/ui_goals_probe.py   |   just probe ui-goals
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
PLAIN_DONE = {"content": "Here are the trade-offs for that objective change.", **_META}


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


async def _inject_auth_and_navigate(page, base: str, token: str) -> bool:
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({"state": {"accessToken": token, "refreshToken": None,
                                       "user": FAKE_USER}, "version": 0})
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        sessionStorage.setItem('af-booted', '1');
    }}""")
    await page.goto(f"{base}/goals", wait_until="networkidle")
    return "/login" not in page.url


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()
    posted = {"concierge": False}

    await page.route("**/api/v1/iam/me", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(FAKE_USER)))
    await page.route("**/api/v1/health/boot/sync-stream", lambda r: r.fulfill(
        status=200, content_type="text/event-stream", body=""))
    await page.route("**/api/v1/health/boot", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"services": [
            {"key": "backend", "label": "Backend", "status": "ok", "detail": "online"}]})))

    async def _concierge(route) -> None:
        posted["concierge"] = True
        await route.fulfill(status=200, content_type="text/event-stream", body=_sse(PLAIN_DONE))

    await page.route("**/api/v1/concierge", _concierge)

    try:
        print("\n── Auth + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached /goals (not /login)", on_app, page.url)
        if not on_app:
            return False
        await page.wait_for_selector(".of-calmar", timeout=15_000)
        body = await page.evaluate("() => document.body.innerText")

        print("\n── Calmar hero + drawdown guard")
        _record("Calmar hero renders 2.4×", "2.4" in body and "×" in body)
        _record("Band shows target 3.0 / floor 2.0", "3.0" in body and "2.0" in body)
        soft = await page.locator(".of-meter .mk.soft").count()
        hard = await page.locator(".of-meter .mk.hard").count()
        _record("Drawdown meter has −12 soft + −20 hard marks", soft >= 1 and hard >= 1)
        await page.screenshot(path=str(SHOT_DIR / "goals-01-default.png"))

        print("\n── Honest-pending (dashed, never a faked 0%)")
        pending = await page.locator(".of-edgetrack.of-pending").count()
        _record("Edges render as a dashed pending track", pending >= 1
                and "pending" in body.lower())
        _record('Self-funding says "not yet covered"', "not yet covered" in body)

        print("\n── First-run toggle → Calmar pending '—'")
        await page.get_by_role("button", name="first-run · pending").click()
        await page.wait_for_timeout(250)
        big = await page.locator(".of-calmar .big").inner_text()
        _record("First-run flips Calmar to pending '—'", "—" in big)
        await page.get_by_role("button", name="default", exact=True).click()
        await page.wait_for_timeout(150)

        print("\n── Propose change → chat (never a silent write)")
        await page.get_by_role("button", name="Propose change →").click()
        await page.wait_for_function("""() => {
            const a = document.querySelector('[aria-label="Alpha chat"]');
            return a && getComputedStyle(a).pointerEvents !== 'none';
        }""", timeout=6_000)
        await page.wait_for_timeout(400)
        _record("Propose opens chat + routes a prompt (no silent write)", posted["concierge"])
        await page.screenshot(path=str(SHOT_DIR / "goals-02-propose.png"))

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

    print(f"Goals UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
