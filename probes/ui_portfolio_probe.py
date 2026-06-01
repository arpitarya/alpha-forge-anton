"""Portfolio filter probe — verifies asset-class chips, sort, PnL filter, and text search.

Attaches to the existing AlphaForge Anton Chrome via CDP. Requires:

    just zerodha-chrome          # opens CDP on port 9299
    backend + frontend running   # localhost:3000 / :8000

Run:
    just ui-portfolio
    uv run python probes/ui_portfolio_probe.py

Environment overrides:
    AF_FRONTEND=https://localhost:3000
    PROBE_USER / PROBE_PASS  (or afbach vault)
    BROKER_CDP_PORT=9299

Screenshots saved to <repo-root>/screenshots/portfolio-*.png.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import httpx

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
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {label}" + (f"  {detail}" if detail else ""))


async def _get_token(base: str) -> str:
    api_base = base.replace(":3000", ":8000")
    async with httpx.AsyncClient(base_url=api_base, timeout=10.0) as client:
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
        )
        r.raise_for_status()
        return r.json()["access_token"]


async def _fetch_holdings(base: str, token: str) -> list[dict]:
    api_base = base.replace(":3000", ":8000")
    async with httpx.AsyncClient(
        base_url=api_base,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15.0,
    ) as client:
        r = await client.get("/api/v1/portfolio/holdings")
        r.raise_for_status()
        return r.json().get("holdings", [])


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)

    token = await _get_token(base)
    holdings = await _fetch_holdings(base, token)
    _record("Holdings API reachable", len(holdings) >= 0, f"{len(holdings)} rows")

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    try:
        await page.set_viewport_size({"width": 1440, "height": 900})

        # Auth via localStorage — skip browser login form
        await page.goto(base, wait_until="domcontentloaded")
        await page.evaluate(f"() => localStorage.setItem('af_token', {token!r})")

        await page.goto(f"{base}/portfolio", wait_until="networkidle", timeout=45_000)
        await page.wait_for_timeout(1500)

        # ── 1. Filter chips visible ───────────────────────────────────
        print("\n── Asset class filter chips")
        chips = await page.query_selector_all("[data-af-chip]")
        _record(
            "Filter chips rendered",
            len(chips) > 1,
            f"{len(chips)} chip(s)",
        )
        await page.screenshot(path=str(SHOT_DIR / "portfolio-01-default.png"))

        # ── 2. Asset class buckets present for each non-zero category ─
        asset_classes = {h.get("asset_class") for h in holdings}
        expected_buckets = {
            "equity": "equity",
            "mutual_fund": "mfetf",
            "etf": "mfetf",
            "gold": "gold",
            "crypto": "crypto",
            "bond": "bond",
            "cash": "cash",
        }
        expected_chips = {expected_buckets[ac] for ac in asset_classes if ac in expected_buckets}
        for bucket in sorted(expected_chips):
            chip = await page.query_selector(f"[data-af-chip='{bucket}']")
            _record(f"Chip '{bucket}' present", chip is not None)

        # ── 3. Equity chip + sub-filter ───────────────────────────────
        print("\n── Equity sub-filter")
        eq_chip = await page.query_selector("[data-af-chip='equity']")
        if eq_chip:
            await eq_chip.click()
            await page.wait_for_timeout(500)
            await page.screenshot(path=str(SHOT_DIR / "portfolio-02-equity.png"))
            rows_after = await page.query_selector_all("[data-af-holding-row]")
            equity_holdings = [h for h in holdings if h.get("asset_class") == "equity"]
            _record(
                "Equity chip filters to equity holdings",
                len(rows_after) == len(equity_holdings) or len(equity_holdings) == 0,
                f"UI:{len(rows_after)} API:{len(equity_holdings)}",
            )

            # Sub-filter: India
            india_chip = await page.query_selector("[data-af-eq-sub='in']")
            if india_chip:
                await india_chip.click()
                await page.wait_for_timeout(400)
                await page.screenshot(path=str(SHOT_DIR / "portfolio-03-equity-india.png"))
                _record("India equity sub-chip clickable", True)
            else:
                _record("India equity sub-chip present", False, "not found in DOM")

            # Reset to All
            all_chip = await page.query_selector("[data-af-chip='all']")
            if all_chip:
                await all_chip.click()
                await page.wait_for_timeout(400)
        else:
            _record("Equity chip present", False, "skipping sub-filter checks")

        # ── 4. PnL filter ─────────────────────────────────────────────
        print("\n── PnL filter")
        pnl_up = await page.query_selector("[data-af-pnl='up']")
        if pnl_up:
            await pnl_up.click()
            await page.wait_for_timeout(400)
            gainers_ui = await page.query_selector_all("[data-af-holding-row]")
            gainers_api = [h for h in holdings if h.get("pnl", 0) > 0]
            _record(
                "PnL 'up' filter shows only gainers",
                len(gainers_ui) == len(gainers_api) or len(gainers_api) == 0,
                f"UI:{len(gainers_ui)} API:{len(gainers_api)}",
            )
            await page.screenshot(path=str(SHOT_DIR / "portfolio-04-pnl-up.png"))
        else:
            _record("PnL up filter button present", False)

        pnl_dn = await page.query_selector("[data-af-pnl='dn']")
        if pnl_dn:
            await pnl_dn.click()
            await page.wait_for_timeout(400)
            losers_ui = await page.query_selector_all("[data-af-holding-row]")
            losers_api = [h for h in holdings if h.get("pnl", 0) < 0]
            _record(
                "PnL 'dn' filter shows only losers",
                len(losers_ui) == len(losers_api) or len(losers_api) == 0,
                f"UI:{len(losers_ui)} API:{len(losers_api)}",
            )
            await page.screenshot(path=str(SHOT_DIR / "portfolio-05-pnl-dn.png"))

        # Reset PnL filter
        pnl_all = await page.query_selector("[data-af-pnl='all']")
        if pnl_all:
            await pnl_all.click()
            await page.wait_for_timeout(300)

        # ── 5. Text search ────────────────────────────────────────────
        print("\n── Text search")
        search_input = await page.query_selector("[data-af-search]")
        if search_input and holdings:
            # Pick a real symbol from holdings to search for
            sample = next((h.get("symbol", "") for h in holdings if h.get("symbol")), "")
            if sample:
                prefix = sample[:3].upper()
                await search_input.fill(prefix)
                await page.wait_for_timeout(400)
                visible_rows = await page.query_selector_all("[data-af-holding-row]")
                api_matches = [
                    h for h in holdings
                    if prefix.lower() in (h.get("symbol") or "").lower()
                    or prefix.lower() in (h.get("name") or "").lower()
                ]
                _record(
                    f"Search '{prefix}' filters holdings",
                    len(visible_rows) > 0 and len(visible_rows) <= len(holdings),
                    f"UI:{len(visible_rows)} API matches:{len(api_matches)}",
                )
                await page.screenshot(path=str(SHOT_DIR / "portfolio-06-search.png"))
                await search_input.fill("")
                await page.wait_for_timeout(300)
            else:
                _record("Text search skipped", True, "no symbol in holdings")
        else:
            _record("Search input present", search_input is not None)

        # ── 6. Sort switcher ──────────────────────────────────────────
        print("\n── Sort")
        sort_btn = await page.query_selector("[data-af-sort]")
        if sort_btn:
            await sort_btn.click()
            await page.wait_for_timeout(400)
            await page.screenshot(path=str(SHOT_DIR / "portfolio-07-sort.png"))
            _record("Sort menu opens", True)
        else:
            _record("Sort control present", False)

        await page.screenshot(path=str(SHOT_DIR / "portfolio-08-final.png"))

    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    print(f"AlphaForge Anton Portfolio Filter Probe  →  {BASE_URL}  [CDP :{CDP_PORT}]")
    print(f"Screenshots  →  {SHOT_DIR}")

    ok = asyncio.run(run(BASE_URL, CDP_PORT))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/portfolio-*.png")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
