"""Capture screenshots of the terminal, portfolio, and preferences pages.

Attaches to the existing AlphaForge Chrome via CDP (same session as the broker
probes) and writes PNGs to <repo-root>/screenshots/. Requires:

    just zerodha-chrome          # CDP on :9299
    backend + frontend running   # default localhost:3000 / :8000

Run:
    uv run python probes/ui_screens.py
"""

from __future__ import annotations

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
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

PAGES: list[tuple[str, str]] = [
    ("terminal",    "/"),
    ("portfolio",   "/portfolio"),
    ("preferences", "/preferences"),
]


async def login(page, base: str) -> None:
    """Get a token from the API and stash it in localStorage so AuthGuard lets us in."""
    import httpx  # noqa: PLC0415

    api_base = base.replace(":3000", ":8000")
    async with httpx.AsyncClient(base_url=api_base, timeout=10.0) as client:
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
        )
        r.raise_for_status()
        token = r.json()["access_token"]

    await page.goto(base, wait_until="domcontentloaded")
    await page.evaluate(f"() => localStorage.setItem('af_token', {token!r})")


async def run(base: str, cdp_port: int) -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()
    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await login(page, base)
        for label, path in PAGES:
            url = base + path
            await page.goto(url, wait_until="networkidle", timeout=45_000)
            # Wait for the main header to mount — confirms React tree is up.
            try:
                await page.wait_for_selector("header[data-af-top], main", timeout=20_000)
            except Exception:  # noqa: BLE001
                pass
            await page.wait_for_timeout(1500)  # let pulses / count-ups settle
            out = SHOT_DIR / f"{label}.png"
            await page.screenshot(path=str(out), full_page=False)
            print(f"  ✓ {label:<11} → {out.relative_to(Path.cwd()) if str(out).startswith(str(Path.cwd())) else out}")
    finally:
        await page.close()
        await pw.stop()


def main() -> None:
    print(f"AlphaForge UI screens → {BASE_URL}  [CDP :{CDP_PORT}]")
    print(f"Output                → {SHOT_DIR}")
    asyncio.run(run(BASE_URL, CDP_PORT))


if __name__ == "__main__":
    main()
