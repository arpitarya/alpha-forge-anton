"""Fux graph viewer probe — opens graph.html and verifies every feature works.

Covers the Solar Terminal viewer end to end: it loads the real `.fux/out/graph.html`,
lets the force simulation settle, and asserts each feature actually behaves:

    · page loads, canvas sized + rendered, stats wired to real data
    · the simulation cools and HOLDS STILL (no perpetual jitter)
    · lens grid (Knowledge / Communities / Heat / Path) switches modes
    · node-type meters + edge-language legend toggle visibility
    · search yields a clickable hit list that selects + centres a node
    · clicking a node opens the inspector with a "governed by" section
    · governance ledger lists knowledge→code links and collapses/expands
    · minimap overview renders with a viewport frame
    · Micro/Macro semantic zoom collapses to community super-nodes + drills in
    · shortest-path mode finds a route; god nodes + knowledge layer present
    · markdown export buttons give feedback

Run:
    just probe fux-graph
    uv run python probes/ui_fux_graph_probe.py [--graph PATH] [--cdp URL]

By default it launches its own headless Chromium. Pass --cdp to drive an
already-running visible Chrome (e.g. the :9299 session) and watch it; in that
mode the browser is left open on exit. Screenshots → <repo-root>/screenshots/.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

GRAPH_HTML = Path(__file__).resolve().parent.parent / ".fux" / "out" / "graph.html"
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {label}" + (f"  — {detail}" if detail else ""))


async def run(graph_path: Path, cdp: str | None = None) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_url = graph_path.as_uri()
    console_errors: list[str] = []

    async with async_playwright() as pw:
        if cdp:
            browser = await pw.chromium.connect_over_cdp(cdp)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await ctx.new_page()
            # Do NOT force a viewport over CDP — that leaves the tab emulating a size
            # that may not match the real window, pushing fixed/edge UI off-screen.
        else:
            browser = await pw.chromium.launch(headless=True, args=["--allow-file-access-from-files"])
            ctx = await browser.new_context(viewport={"width": 1600, "height": 1000})
            page = await ctx.new_page()

        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        # ── 1. load ───────────────────────────────────────────────────────────
        try:
            await page.goto(file_url, wait_until="networkidle", timeout=30_000)
            _record("page loads without network error", True)
        except Exception as exc:  # noqa: BLE001
            _record("page loads without network error", False, str(exc))
            if not cdp:
                await browser.close()
            return False

        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SHOT_DIR / "fux-graph-01-load.png"))

        # ── 2. canvas + stats + filters ───────────────────────────────────────
        cv_w, cv_h = await page.evaluate("() => [cv.width, cv.height]")
        _record("canvas has non-zero width", cv_w > 0, f"width={cv_w}")
        _record("canvas has non-zero height", cv_h > 0, f"height={cv_h}")

        stats_text = await page.text_content("#stats") or ""
        _record("stats bar populated", "nodes" in stats_text and "edges" in stats_text, repr(stats_text[:70]))

        n_node_cbs = await page.eval_on_selector_all("[data-t]", "els => els.length")
        _record("node-type filters rendered", n_node_cbs > 0, f"{n_node_cbs} types")
        n_edge_cbs = await page.eval_on_selector_all("[data-e]", "els => els.length")
        _record("edge-type legend rendered", n_edge_cbs > 0, f"{n_edge_cbs} types")

        has_pixels = await page.evaluate("""() => { const d=cv.getContext('2d')
            .getImageData(0,0,cv.width,cv.height).data; return d.some(v => v !== 0); }""")
        _record("canvas has rendered pixels", has_pixels)

        # ── 3. the simulation settles and HOLDS STILL ─────────────────────────
        # Cooling is frame-count based, so wall-clock time varies with the tab's
        # frame rate — poll until it settles rather than assuming a fixed delay.
        await page.bring_to_front()
        s1 = {"run": True, "a": 1.0}
        for _ in range(40):
            await page.wait_for_timeout(1_000)
            s1 = await page.evaluate("() => ({run:running, a:alpha, sum:nodes.reduce((s,n)=>s+n.x+n.y,0)})")
            if not s1["run"]:
                break
        await page.wait_for_timeout(1_200)
        s2 = await page.evaluate("() => ({sum:nodes.reduce((s,n)=>s+n.x+n.y,0)})")
        drift = abs(s2["sum"] - s1.get("sum", 0))
        _record("simulation cools and stops", (not s1["run"]) and s1["a"] == 0,
                f"alpha={s1['a']:.4f} running={s1['run']}")
        _record("nodes hold still once settled", drift < 1.0, f"position drift={drift:.3f}")
        await page.screenshot(path=str(SHOT_DIR / "fux-graph-02-settled.png"))

        # ── 4. lens grid switches modes ───────────────────────────────────────
        n_lenses = await page.eval_on_selector_all("#lensgrid .lens", "els => els.length")
        _record("lens grid has 4 lenses", n_lenses == 4, f"{n_lenses} lenses")
        await page.click('#lensgrid .lens[data-lens="community"]')
        _record("Communities lens activates", await page.evaluate("() => lens") == "community")
        await page.click('#lensgrid .lens[data-lens="heat"]')
        _record("Heat lens activates", await page.evaluate("() => lens") == "heat")
        await page.click('#lensgrid .lens[data-lens="know"]')
        _record("Knowledge lens activates", await page.evaluate("() => lens") == "know")

        # ── 5. node-type + edge filters toggle ────────────────────────────────
        h0 = await page.evaluate("() => hidden.size")
        await page.click("#filters .meter")
        h1 = await page.evaluate("() => hidden.size")
        await page.click("#filters .meter")
        h2 = await page.evaluate("() => hidden.size")
        _record("node-type filter toggles visibility", h1 == h0 + 1 and h2 == h0, f"{h0}→{h1}→{h2}")
        e0 = await page.evaluate("() => hiddenE.size")
        await page.click("#efilters .lg-row")
        e1 = await page.evaluate("() => hiddenE.size")
        await page.click("#efilters .lg-row")
        _record("edge-type filter toggles visibility", e1 == e0 + 1, f"{e0}→{e1}")

        # ── 6. search → clickable hits → jump ─────────────────────────────────
        await page.fill("#q", "a")
        await page.wait_for_timeout(150)
        n_hits = await page.eval_on_selector_all("#qhits .hit", "els => els.length")
        _record("search produces clickable hit list", n_hits > 0, f"{n_hits} hits shown")
        if n_hits:
            await page.click("#qhits .hit")
            await page.wait_for_timeout(120)
            _record("clicking a hit selects that node", await page.evaluate("() => selected") is not None)
        await page.fill("#q", "")
        await page.wait_for_timeout(100)

        # ── 7. freeze + inspector on node click ───────────────────────────────
        await page.evaluate("() => { running=false; selected=null;"
                            " view.k=1.1; view.x=0; view.y=0; clearDetail(); }")
        await page.wait_for_timeout(120)
        _record("inspector hidden before node click", not await page.is_visible("#agentrow"))
        target = await page.evaluate("""() => { let best=null,bd=-1;
            for(const n of nodes){ if(!visible(n)) continue; const d=deg[n.id]||0; if(d>bd){bd=d;best=n;} }
            const p=T(best), r=cv.getBoundingClientRect(); return {x:r.x+p.x, y:r.y+p.y, label:best.label}; }""")
        if target:
            await page.mouse.click(target["x"], target["y"])
            await page.wait_for_timeout(150)
        _record("inspector opens on node click", await page.is_visible("#agentrow"),
                target["label"] if target else "no node")
        detail = await page.text_content("#detail") or ""
        _record("inspector shows node metadata", "community" in detail and "degree" in detail)
        _record("inspector surfaces 'governed by' for code", "governed by" in detail)
        await page.screenshot(path=str(SHOT_DIR / "fux-graph-03-inspect.png"))

        # ── 8. right aside starts collapsed; floating minimap shows instead ────
        default_collapsed = await page.evaluate("() => document.getElementById('right').classList.contains('collapsed')")
        _record("right aside collapsed by default", default_collapsed)
        fmm_w = await page.evaluate("() => document.getElementById('fmm').width")
        fmm_shown = await page.is_visible("#floatmm")
        _record("floating minimap shows when collapsed", fmm_shown and fmm_w > 0, f"fmm={fmm_w}px")
        w_collapsed = await page.evaluate("() => cv.parentElement.clientWidth")
        # expand the aside to inspect the in-rail panels
        await page.click("#railtab")
        await page.wait_for_timeout(300)
        w_expanded = await page.evaluate("() => cv.parentElement.clientWidth")
        _record("expanding aside narrows the canvas", w_collapsed > w_expanded, f"{w_collapsed}→{w_expanded}px")

        # ── 9. governance ledger + collapse ───────────────────────────────────
        frac = await page.text_content("#led-frac") or ""
        n_rows = await page.eval_on_selector_all("#ledbody .lrow", "els => els.length")
        empty = await page.eval_on_selector_all("#ledbody .led-empty", "els => els.length")
        _record("governance ledger populated", (n_rows > 0 or empty > 0) and "of" in frac,
                f"{n_rows} rules · '{frac.strip()}'")
        await page.click("#ledhead")
        await page.wait_for_timeout(120)
        collapsed = await page.evaluate("() => document.getElementById('led').classList.contains('collapsed')")
        body_hidden = not await page.is_visible("#ledbody")
        await page.click("#ledhead")
        await page.wait_for_timeout(120)
        reopened = await page.is_visible("#ledbody")
        _record("ledger collapses and re-expands", collapsed and body_hidden and reopened)

        # ── 10. rail minimap (now that the aside is expanded) ─────────────────
        mm_w = await page.evaluate("() => document.getElementById('mm').width")
        mmview_w = await page.evaluate("() => document.getElementById('mmview').offsetWidth")
        _record("rail minimap renders with viewport frame", mm_w > 0 and mmview_w > 0, f"mm={mm_w} frame={mmview_w}px")

        # collapse it again — canvas widens, floating minimap returns
        w_expanded = await page.evaluate("() => cv.parentElement.clientWidth")
        await page.click("#railtab")
        await page.wait_for_timeout(300)
        re_collapsed = await page.evaluate("() => document.getElementById('right').classList.contains('collapsed')")
        w_recollapsed = await page.evaluate("() => cv.parentElement.clientWidth")
        _record("collapsing aside widens the canvas", re_collapsed and w_recollapsed > w_expanded,
                f"{w_expanded}→{w_recollapsed}px")

        # ── 11. Macro / Micro zoom (real nodes either way, no super-nodes) ────
        await page.click("#bmacro")
        await page.wait_for_timeout(700)
        k_macro = await page.evaluate("() => view.k")
        vis_macro = await page.evaluate("() => nodes.filter(visible).length")
        _record("Macro zooms out to the real-node overview", k_macro < 0.7 and vis_macro > 100,
                f"k={k_macro:.2f} · {vis_macro} nodes shown")
        await page.screenshot(path=str(SHOT_DIR / "fux-graph-04-macro.png"))
        await page.click("#bmicro")
        await page.wait_for_timeout(300)
        k_micro = await page.evaluate("() => view.k")
        _record("Micro zooms back in", k_micro > k_macro, f"k {k_macro:.2f}→{k_micro:.2f}")

        # ── 12. shortest path ─────────────────────────────────────────────────
        path_len = await page.evaluate("""() => { let best=null,bd=-1;
            for(const n of nodes){ const d=deg[n.id]||0; if(d>bd){bd=d;best=n;} }
            const nb=adj[best.id][0] && adj[best.id][0][0]; if(!nb) return 0;
            const p=shortestPath(best.id, nb); return p ? p.length : 0; }""")
        _record("shortest-path finds a route", path_len >= 2, f"path length={path_len}")
        await page.click('#lensgrid .lens[data-lens="path"]')
        pmode = await page.evaluate("() => pathMode")
        await page.click('#lensgrid .lens[data-lens="path"]')
        _record("path mode toggles on", pmode)

        # ── 13. god nodes + knowledge layer present ───────────────────────────
        counts = await page.evaluate("""() => ({gods:nodes.filter(isGod).length,
            know:nodes.filter(isKnow).length, gov:+document.getElementById('st-gov').textContent}) """)
        _record("hub/god nodes emphasised", counts["gods"] > 0, f"{counts['gods']} hubs")
        _record("knowledge layer present + govern count wired", counts["know"] > 0,
                f"{counts['know']} knowledge nodes · {counts['gov']} governs")

        # ── 14. markdown export feedback ──────────────────────────────────────
        # the copy-row lives in the inspector, so select a node to reveal it first
        await page.evaluate("() => { selected = nodes[0].id; showDetail(byId[selected]); }")
        await page.wait_for_timeout(80)
        await page.click("#bexport")
        await page.wait_for_timeout(150)
        _record("Copy-subgraph shows feedback", await page.is_visible("#toast"))
        # the governed-subgraph button is in the right rail — make sure it's open
        await page.evaluate("() => { const r=document.getElementById('right');"
                            " if(r.classList.contains('collapsed')){ r.classList.remove('collapsed'); applyRightState(); } }")
        await page.wait_for_timeout(250)
        await page.click("#bgov")
        await page.wait_for_timeout(150)
        _record("Copy-governed-subgraph shows feedback", await page.is_visible("#toast"))

        # tidy up the view for the parting screenshot
        await page.evaluate("() => { setLens('know'); clearFocus(); clearPath();"
                            " selected=null; clearDetail(); fit(); }")
        await page.wait_for_timeout(200)
        _record("no JS console errors", not console_errors,
                "; ".join(console_errors[:3]) if console_errors else "")
        await page.screenshot(path=str(SHOT_DIR / "fux-graph-05-final.png"))

        if not cdp:
            await browser.close()
        else:
            print(f"\n  (CDP mode: leaving browser open — graph is on screen at {file_url})")

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fux graph viewer probe")
    parser.add_argument("--graph", type=Path, default=GRAPH_HTML,
                        help="Path to graph.html (default: .fux/out/graph.html)")
    parser.add_argument("--cdp", nargs="?", const="http://localhost:9222", default=None,
                        help="Connect to a running Chrome over CDP (visible browser) "
                             "instead of launching headless. Default endpoint http://localhost:9222.")
    args = parser.parse_args()

    if not args.graph.exists():
        print(f"❌ graph.html not found: {args.graph}", file=sys.stderr)
        sys.exit(1)

    mode = f"CDP {args.cdp}" if args.cdp else "headless"
    print(f"AlphaForge Anton  Fux Graph Probe  ({mode})  →  {args.graph.as_uri()}")
    ok = asyncio.run(run(args.graph, cdp=args.cdp))
    passed = sum(1 for _, o, _ in _results if o)
    print(f"\n── Summary\n  {passed}/{len(_results)} checks passed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
