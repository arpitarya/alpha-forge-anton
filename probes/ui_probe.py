"""Playwright UI probe — exercises the AlphaForge frontend auth + navigation flow.

Attaches to the existing AlphaForge Chrome via CDP — the same session used by
the broker probes (Zerodha, Groww, Wint Wealth). Start Chrome once with:

    just zerodha-chrome          # opens CDP on port 9299

Then run this probe (backend + frontend must be running):

    just ui-probe                          # CDP :9299 (default)
    uv run python probes/ui_probe.py
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

from app.modules.brokers._cdp import connect_existing_chrome

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


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()
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
        except Exception as exc:  # noqa: BLE001
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

        # ── 4. Dashboard ──────────────────────────────────────────────
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

        # ── 5a. Portfolio data quality ─────────────────────────────────
        print("\n── Portfolio data quality")

        # Check holdings API responds with data
        import httpx  # noqa: PLC0415

        token_val = await page.evaluate("() => localStorage.getItem('af_token')")
        headers = {"Authorization": f"Bearer {token_val}"} if token_val else {}
        api_base = base.replace(":3000", ":8000")
        async with httpx.AsyncClient(base_url=api_base, headers=headers, timeout=10.0) as client:
            try:
                r = await client.get("/api/portfolio/holdings")
                _record("Holdings API responds", r.status_code < 400, f"HTTP {r.status_code}")
                if r.status_code < 400:
                    payload = r.json()
                    totals = payload.get("totals", {})
                    holdings = payload.get("holdings", [])
                    _record("Holdings list non-empty", len(holdings) > 0, f"{len(holdings)} holdings")
                    _record("Invested > 0", totals.get("invested", 0) > 0, f"₹{totals.get('invested', 0):,.0f}")
                    _record("Current value > 0", totals.get("current_value", 0) > 0, f"₹{totals.get('current_value', 0):,.0f}")

                    # Per-broker data checks
                    for slug in ("zerodha", "groww", "wintwealth"):
                        broker_holdings = [h for h in holdings if h.get("source") == slug]
                        if broker_holdings:
                            bad_pnl_pct = [
                                h for h in broker_holdings
                                if h.get("invested", 0) > 0
                                and abs(h.get("pnl_pct", 0) - (
                                    (h["current_value"] - h["invested"]) / h["invested"] * 100
                                )) > 0.01
                            ]
                            _record(
                                f"{slug}: pnl_pct consistent with invested/current_value",
                                len(bad_pnl_pct) == 0,
                                f"{len(bad_pnl_pct)} inconsistent row(s)" if bad_pnl_pct else "",
                            )
                            ltp_zero = [h for h in broker_holdings if h.get("last_price", 0) == 0]
                            _record(
                                f"{slug}: no holdings with ltp=0",
                                len(ltp_zero) == 0,
                                f"{len(ltp_zero)} row(s) with ltp=0" if ltp_zero else "",
                            )
            except Exception as e:  # noqa: BLE001
                _record("Holdings API reachable", False, str(e))

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
        await page.close()   # leave the rest of the Chrome session intact
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=BASE_URL, help=f"Frontend URL (default: {BASE_URL})")
    parser.add_argument(
        "--cdp-port", type=int, default=CDP_PORT,
        help=f"CDP port of the existing AlphaForge Chrome (default: {CDP_PORT})",
    )
    args = parser.parse_args()

    print(f"AlphaForge UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    print(f"Screenshots          →  {SHOT_DIR}")

    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
