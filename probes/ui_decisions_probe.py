"""CDP probe — the Decisions surface (replayable prove-it ledger) at /decisions.

Attaches to the existing Chrome CDP session (:9299), injects a dev JWT, and asserts
what the browser renders on Track-U MOCK data (no live dependency):

  1. Reaching /decisions (not redirected to /login)
  2. The decision-journal rows render
  3. Calibration scoreboard shows 13 cleared · 4 stop · 3 open
  4. REPLAY is enabled only on replayable rows (one mock row is not replayable)
  5. Replaying an enabled row shows the deterministic read-only re-run summary

Run:  uv run python probes/ui_decisions_probe.py   |   just probe ui-decisions
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
    """Auth, then reach /decisions WITHOUT racing the auth guard. `zustand/persist`
    rehydrates asynchronously, so a full `goto(/decisions)` runs `AuthGuard` with a null
    token and bounces to /login. Instead: seed storage before any app script (init
    script), land on / so the store rehydrates, then CLIENT-navigate via the in-app
    Decisions button — the hydrated store stays in memory across the SPA transition."""
    auth_state = json.dumps({"state": {"accessToken": token, "refreshToken": None,
                                       "user": FAKE_USER}, "version": 0})
    await page.add_init_script(f"""() => {{ try {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        sessionStorage.setItem('af-booted', '1');
    }} catch (e) {{}} }}""")
    await page.goto(base, wait_until="domcontentloaded")
    decisions = page.get_by_role("button", name="Decisions")
    await decisions.first.wait_for(timeout=15_000)
    await decisions.first.click()
    await page.wait_for_url("**/decisions", timeout=10_000)
    return "/decisions" in page.url


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
            {"key": "backend", "label": "Backend", "status": "ok", "detail": "online"}]})))

    try:
        print("\n── Auth + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached /decisions (not /login)", on_app, page.url)
        if not on_app:
            return False
        await page.wait_for_selector(".of-ledger", timeout=15_000)
        body = await page.evaluate("() => document.body.innerText")

        print("\n── Ledger + calibration")
        rows = await page.locator(".of-drow").count()
        _record("Decision-journal rows render", rows >= 4, f"{rows} rows")
        nums = await page.locator(".of-calib .cell .n").all_inner_texts()
        _record("Calibration shows 13 · 4 · 3", nums[:3] == ["13", "4", "3"], str(nums))
        # chips render UPPERCASE via CSS text-transform (innerText reflects it) — match lower.
        oc = body.lower()
        _record("Outcome chips render (cleared / hit stop / open)",
                "cleared cone" in oc and "hit stop" in oc and "open" in oc)
        await page.screenshot(path=str(SHOT_DIR / "decisions-01-ledger.png"))

        print("\n── Replay gating")
        disabled = await page.locator(".of-replay:disabled").count()
        enabled = await page.locator(".of-replay:not([disabled])").count()
        _record("REPLAY disabled on the non-replayable row", disabled == 1, f"{disabled} disabled")
        _record("REPLAY enabled on replayable rows", enabled >= 3, f"{enabled} enabled")

        await page.locator(".of-replay:not([disabled])").first.click()
        await page.wait_for_selector(".of-replay-out", timeout=4_000)
        out = await page.locator(".of-replay-out").first.inner_text()
        _record("Replay shows the read-only re-run summary", "byte-identical" in out)
        await page.screenshot(path=str(SHOT_DIR / "decisions-02-replay.png"))

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

    print(f"Decisions UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
