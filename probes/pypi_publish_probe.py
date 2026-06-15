"""Verify the sibling tools (fux-engine, cage-flux) are live on PyPI.

Attaches to the running Chrome over CDP (:9299) and loads each project's public
PyPI page, asserting the package exists and reading its latest published version.
This is the release-health counterpart to github_publish_probe.py: GitHub says the
publish *ran*, PyPI says the artifact actually *landed*.

Run:
    just probe pypi-publish
    uv run python probes/pypi_publish_probe.py

Requires: CDP Chrome on :9299 (`just zerodha-chrome`). No login needed — PyPI
project pages are public. Screenshots saved to <repo-root>/screenshots/.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome

CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

# (display name, PyPI distribution name)
PACKAGES = [("fux", "fux-engine"), ("cage", "cage-flux")]

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    print(f"  {'✓' if ok else '✗'}  {label}" + (f"  {detail}" if detail else ""))


async def _check_package(ctx, name: str, dist: str) -> None:  # noqa: ANN001
    page = await ctx.new_page()
    try:
        url = f"https://pypi.org/project/{dist}/"
        resp = await page.goto(url, wait_until="domcontentloaded")

        status = resp.status if resp else 0
        if status == 404:
            await page.screenshot(path=str(SHOT_DIR / f"pypi-{dist}.png"))
            _record(f"{name}: {dist} on PyPI", False, "404 — not published")
            return

        # PyPI renders "<dist> <version>" in <h1 class="package-header__name">.
        header = page.locator("h1.package-header__name")
        try:
            await header.wait_for(timeout=10000)
        except Exception:  # noqa: BLE001
            pass
        await page.screenshot(path=str(SHOT_DIR / f"pypi-{dist}.png"))
        text = (await header.inner_text()).strip() if await header.count() else ""
        ok = dist in text and any(c.isdigit() for c in text)
        version = text.replace(dist, "").strip() or "?"
        _record(f"{name}: {dist} live on PyPI", ok, f"latest {version}" if ok else f"header={text!r}")
    finally:
        await page.close()


async def run(cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    try:
        for name, dist in PACKAGES:
            await _check_package(ctx, name, dist)
    finally:
        await pw.stop()
    return all(ok for _, ok, _ in _results)


def main() -> None:
    print(f"PyPI Publish Probe  →  pypi.org  [CDP :{CDP_PORT}]")
    ok = asyncio.run(run(CDP_PORT))
    passed = sum(1 for _, o, _ in _results if o)
    print(f"\n── Summary\n  {passed}/{len(_results)} packages live")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
