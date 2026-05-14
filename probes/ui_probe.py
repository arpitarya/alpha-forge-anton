"""Playwright UI probe — exercises the AlphaForge frontend auth + navigation flow.

By default attaches to the existing AlphaForge Chrome (CDP port 9299, started
via `just zerodha-chrome`). Pass --headless to spin up a fresh browser instead.

Usage:
    just ui-probe                          # CDP, existing Chrome (default)
    just ui-probe --headless               # fresh headless Chromium
    just ui-probe --headed                 # fresh headed Chromium
    uv run python probes/ui_probe.py --cdp-port 9299

Environment overrides:
    AF_FRONTEND=http://localhost:3000
    PROBE_USER=admin
    PROBE_PASS=alphaforge-dev
    BROKER_CDP_PORT=9299

Screenshots are saved to /tmp/alphaforge-probe/.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

BASE_URL = os.getenv("AF_FRONTEND", "http://localhost:3000")
CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
USERNAME = os.getenv("PROBE_USER", "admin")
PASSWORD = os.getenv("PROBE_PASS", "alphaforge-dev")
SHOT_DIR = Path("/tmp/alphaforge-probe")

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {label}" + (f"  {detail}" if detail else ""))


async def _get_page(pw, cdp_port: int | None, headed: bool):  # type: ignore[no-untyped-def]
    """Return (page, browser, playwright, is_cdp) ready for use."""
    if cdp_port is not None:
        from app.modules.brokers._cdp import connect_existing_chrome
        pw_inst, browser = await connect_existing_chrome(cdp_port)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()
        return page, browser, pw_inst, True

    from playwright.async_api import async_playwright
    pw_inst = await async_playwright().start()
    browser = await pw_inst.chromium.launch(headless=not headed)
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
    page = await ctx.new_page()
    return page, browser, pw_inst, False


async def run(base: str, cdp_port: int | None, headed: bool) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    page, browser, pw_inst, is_cdp = await _get_page(None, cdp_port, headed)
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

    try:
        # Clear any stale session so we always test from a clean state
        await page.goto(base, wait_until="domcontentloaded")
        await page.evaluate("() => localStorage.removeItem('af_token')")

        # ── 1. Auth guard ─────────────────────────────────────────────
        print("\n── Auth guard")
        await page.goto(base, wait_until="networkidle")
        login_ok = "/login" in page.url
        _record("/ redirects to /login when unauthenticated", login_ok, page.url)
        await page.screenshot(path=str(SHOT_DIR / "01-login-page.png"))

        if not login_ok:
            print("\n  Login page not reached — is the frontend running?")
            return False

        # ── 2. Login ──────────────────────────────────────────────────
        print("\n── Login")
        await page.fill('input[type="text"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        try:
            await page.wait_for_url(lambda url: "/login" not in url, timeout=10_000)
        except Exception as exc:
            print(f"    (navigation wait: {exc})")

        logged_in = "/login" not in page.url
        _record("Login with dev credentials succeeds", logged_in, page.url)
        await page.screenshot(path=str(SHOT_DIR / "02-dashboard.png"))

        if not logged_in:
            print("\n  Login failed — check backend is running and credentials are correct.")
            return False

        # ── 3. Token stored ───────────────────────────────────────────
        token = await page.evaluate("() => localStorage.getItem('af_token')")
        _record("JWT token in localStorage", bool(token), "present" if token else "MISSING")

        # ── 4. Dashboard API calls ────────────────────────────────────
        print("\n── Dashboard")
        pre = len(console_errors)
        await page.wait_for_timeout(1500)
        new_errs = console_errors[pre:]
        _record("No console errors on dashboard", not new_errs,
                f"{len(new_errs)} error(s)" if new_errs else "")

        # ── 5. Portfolio page ──────────────────────────────────────────
        print("\n── Portfolio")
        resp = await page.goto(f"{base}/portfolio", wait_until="networkidle")
        ok = resp is not None and resp.status < 400
        _record("Portfolio page loads", ok, f"HTTP {resp.status if resp else '?'}")
        await page.screenshot(path=str(SHOT_DIR / "03-portfolio.png"))

        # ── 6. Session persists across reload ─────────────────────────
        print("\n── Session persistence")
        await page.reload(wait_until="networkidle")
        token_after = await page.evaluate("() => localStorage.getItem('af_token')")
        _record("Token persists across reload", bool(token_after) and "/login" not in page.url)

        # ── 7. Logout ─────────────────────────────────────────────────
        print("\n── Logout")
        await page.evaluate("() => localStorage.removeItem('af_token')")
        await page.reload(wait_until="networkidle")
        back_to_login = "/login" in page.url
        _record("Removing token redirects back to /login", back_to_login, page.url)
        await page.screenshot(path=str(SHOT_DIR / "04-after-logout.png"))

    finally:
        if is_cdp:
            await page.close()   # leave the user's Chrome session intact
        else:
            await browser.close()
        await pw_inst.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=BASE_URL, help=f"Frontend URL (default: {BASE_URL})")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--cdp-port", type=int, default=CDP_PORT,
                   help=f"Attach to existing Chrome on this CDP port (default: {CDP_PORT})")
    g.add_argument("--headless", action="store_true",
                   help="Launch fresh headless Chromium instead of using existing Chrome")
    g.add_argument("--headed", action="store_true",
                   help="Launch fresh headed Chromium instead of using existing Chrome")
    args = parser.parse_args()

    cdp_port = None if (args.headless or args.headed) else args.cdp_port
    mode = f"CDP :{cdp_port}" if cdp_port else ("headed" if args.headed else "headless")

    print(f"AlphaForge UI Probe  →  {args.base}  [{mode}]")
    print(f"Screenshots          →  {SHOT_DIR}")

    ok = asyncio.run(run(args.base, cdp_port, args.headed))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
