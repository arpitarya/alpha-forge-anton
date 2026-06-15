"""Verify the sibling tools' release/CI workflows are green on GitHub.

Attaches to the running Chrome over CDP (:9299) — reusing your authenticated
GitHub session — and loads each repo's Actions page for a specific workflow,
reading the latest run's status straight off the rendered runs list.

Covers the two workflows this probe was written to catch regressions in:
  - fux  → Publish to PyPI   (.github/workflows/publish.yml)
  - cage → Python package    (.github/workflows/python-package.yml)

Run:
    just probe github-publish
    uv run python probes/github_publish_probe.py

Requires: CDP Chrome on :9299 (`just zerodha-chrome`), logged in to GitHub in
that browser. Screenshots saved to <repo-root>/screenshots/.
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

# (display name, owner/repo, workflow file)
WORKFLOWS = [
    ("fux publish", "arpitarya/fux", "publish.yml"),
    ("cage CI", "arpitarya/cage", "python-package.yml"),
]

# Each run row carries an aria-label like "completed successfully: Run 22 of CI. <commit>"
# or "failed: Run 6 of Publish to PyPI. <commit>". The first match inside <main> is the
# latest run (GitHub lists newest first); parse the status phrase before the colon.
_LATEST_RUN_JS = r"""
() => {
  const root = document.querySelector('main') || document.body;
  for (const el of root.querySelectorAll('[aria-label]')) {
    const al = el.getAttribute('aria-label') || '';
    const m = al.match(/^(.*?):\s*(Run \d+ of .*)$/);
    if (!m) continue;
    const phrase = m[1].toLowerCase().trim();
    let status = phrase;
    if (phrase.startsWith('completed successfully') || phrase === 'succeeded') status = 'success';
    else if (phrase.startsWith('failed')) status = 'failure';
    else if (phrase.startsWith('cancelled')) status = 'cancelled';
    else if (phrase.startsWith('skipped')) status = 'skipped';
    else if (/(in progress|queued|waiting|pending|requested|running)/.test(phrase)) status = 'in_progress';
    return { status, title: m[2].replace(/\s+/g, ' ').slice(0, 70) };
  }
  return { status: 'unknown', title: '' };
}
"""

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    print(f"  {'✓' if ok else '✗'}  {label}" + (f"  {detail}" if detail else ""))


async def _check_workflow(ctx, name: str, repo: str, wf: str) -> None:  # noqa: ANN001
    page = await ctx.new_page()
    try:
        url = f"https://github.com/{repo}/actions/workflows/{wf}"
        await page.goto(url, wait_until="domcontentloaded")
        try:
            await page.wait_for_selector("main [aria-label*='Run ']", timeout=15000)
        except Exception:  # noqa: BLE001
            pass
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(SHOT_DIR / f"gh-{repo.replace('/', '-')}-{wf}.png"))

        info = await page.evaluate(_LATEST_RUN_JS)
        status, title = info.get("status", "unknown"), info.get("title", "")
        ok = status == "success"
        detail = f"latest={status}" + (f' — "{title}"' if title else "")
        _record(f"{name}: latest run green", ok, detail)
    finally:
        await page.close()


async def run(cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    try:
        for name, repo, wf in WORKFLOWS:
            await _check_workflow(ctx, name, repo, wf)
    finally:
        await pw.stop()
    return all(ok for _, ok, _ in _results)


def main() -> None:
    print(f"GitHub Publish Probe  →  github.com  [CDP :{CDP_PORT}]")
    ok = asyncio.run(run(CDP_PORT))
    passed = sum(1 for _, o, _ in _results if o)
    print(f"\n── Summary\n  {passed}/{len(_results)} workflows green")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
