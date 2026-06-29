"""CDP probe — the process-flow cockpit at /flow, on REAL edge state.

Attaches to the existing Chrome CDP session (:9299), injects a dev JWT, and asserts what
the browser renders from the REAL flow loaders (`flow_service` over the elgar journal):
all 9 stages render for edge-001 with honest per-stage status (Idea/Rule/Test DONE,
Test = KILL, Plan→Watch BLOCKED), and the "New edge" path shows the Idea templates
(Family A/B authorable, C scaffolded). The dev JWT ≠ the backend secret, so values are
minted from the loaders in-process and served through the routes the page fetches.

  1. Reaching /flow (not redirected to /login)
  2. All 9 locked stages render in the rail
  3. edge-001 shows frozen; Test runs the funnel (4 gates, gate-1 FAILED), verdict FAIL
  4. Range renders the downside-first cone (worst-case ES P5 leads)
  5. Plan (on a synthetic surviving edge) renders the sizing constraints + binding
  6. Red-team renders severity-tagged objections + 10th-Man + metering attribution
  7. Approve leads with the worst-case loss; ack-loss-first gates the Approve button
  8. Live prepares copy-only orders (never auto-executes); reconcile lights the staged guard
  9. Watch flags a decayed edge + offers the decay-kill (retire)
 10. "New edge" opens the author panel; Family A/B/C templates render; C is disabled

Run:  uv run python probes/ui_flow_probe.py   |   just probe ui-flow
Screenshots → <repo-root>/screenshots/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import jwt as pyjwt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome
from app.modules.contracts.cone_contract import Cone
from app.modules.contracts.testreport_contract import TestReport
from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.contracts.approval_contract import Calibration
from app.modules.flow import (
    flow_approve,
    flow_live,
    flow_service,
    flow_sizing,
    flow_templates,
    flow_watch,
)
from app.modules.flow.flow_decision_schema import ApproveState
from app.modules.flow.flow_live_schema import Fill
from app.modules.flow.flow_redteam_schema import RedteamObjection, RedteamReport
from app.modules.flow.flow_run import gates_from_report
from app.modules.flow.flow_watch_schema import Observation
from app.modules.flow.flow_run_schema import RunPhase, RunStatus
from app.modules.flow.flow_schema import EdgeListItem, FlowState
from app.modules.flow.flow_sizing_schema import SizingInputs
from app.modules.flow.flow_stages import derive, furthest, stage_defs


def _redteam_done() -> RedteamReport:
    """A canned DONE red-team — the DOM-render fixture (parse/spend covered by flow_redteam_probe)."""
    return RedteamReport(
        phase=RunPhase.DONE,
        objections=[RedteamObjection(severity="high", title="Overfit risk", detail="PBO near 0.5"),
                    RedteamObjection(severity="med", title="Cost drag")],
        tenth_man="Momentum crashes exactly when you need the edge most.",
        runner_ups=["wait for trend confirmation"], tripwires=["NIFTY < 200-DMA"],
        provider="claude-sdk", model="claude-opus-4-8",
    )


def _approve_state() -> ApproveState:
    """The Approve fixture for the synthetic surviving edge — proposal + checklist, undecided."""
    p = flow_approve.proposal_from("a survivor", 62_500.0, 20.0, _redteam_done(), Calibration())
    return ApproveState(
        proposal=p, checklist=flow_approve.exec_checklist(p, 6.25, "fractional-kelly"),
        redteam_ready=True, decision=None, can_decide=True,
    )


def _recon_hard():
    """A reconcile result that breaches the hard guard — fed when the probe submits fills."""
    return flow_live.reconcile(62_500.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=790)])


def _watch_decayed():
    """A decayed watch state — fed when the probe logs a period, so the decay-kill block shows."""
    series = [Observation(period=f"w{i}", return_pct=r) for i, r in enumerate([-3, -4, -5, -2, -6])]
    return flow_watch.analyze(series, expected=2.0)


_PASS_AT = datetime(2026, 6, 28, tzinfo=UTC)


def _pass_flow() -> FlowState:
    """A SYNTHETIC surviving edge — edge-001 is a real KILL, so to exercise the Plan stage
    (sizing unlocks only on a PASS) the probe carries one passing edge as a render fixture."""
    spec = EdgeSpec(
        id="edge-pass",
        hypothesis="a survivor",
        signal="momentum",
        pre_registered_at=_PASS_AT,
    )
    rec = JournalRecord(
        edge_id="edge-pass", run_at=_PASS_AT.isoformat(), gate_reached=3, passed=True
    )
    return FlowState(
        edge_id="edge-pass",
        hypothesis=spec.hypothesis,
        frozen=True,
        spec_ref="elgar://edge/edge-pass",
        stages=derive(spec, rec),
    )


def _done_run() -> RunStatus:
    """A canned DONE run (edge-001's KILL shape) — the DOM-render fixture for Test/Range.
    Compute correctness is covered by flow_run_probe; here we test that the panels render."""
    rep = TestReport(
        edge_id="edge-001",
        gates_passed=[],
        verdict="fail",
        data_provenance="nse-bhavcopy",
    )
    cone = Cone(
        horizon="52w",
        p5=[-1, -4, -7, -11],
        p50=[0, 1, 2, 3],
        p95=[1, 3, 6, 9],
        es_p5=-11.0,
        confidence=0.9,
    )
    return RunStatus(
        job_id="probe-job",
        edge_id="edge-001",
        phase=RunPhase.DONE,
        gates=gates_from_report(rep),
        report=rep,
        cone=cone,
        signature="probe000sig00",
    )


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
    payload = {
        "sub": FAKE_USER["guid"],
        "role": FAKE_USER["role"],
        "email": FAKE_USER["email"],
        "iat": now,
        "exp": now + 3600,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def _dump(models) -> str:
    return json.dumps([m.model_dump(mode="json") for m in models])


async def _inject_auth_and_navigate(page, base: str, token: str) -> bool:
    """Auth, then reach /flow via the in-app Flow nav button — never a direct goto
    (the auth store rehydrates async; a full goto bounces to /login). See ui-probe-spa-auth-nav."""
    auth_state = json.dumps(
        {
            "state": {"accessToken": token, "refreshToken": None, "user": FAKE_USER},
            "version": 0,
        }
    )
    await page.add_init_script(f"""() => {{ try {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        sessionStorage.setItem('af-booted', '1');
    }} catch (e) {{}} }}""")
    await page.goto(base, wait_until="domcontentloaded")
    flow = page.get_by_role("button", name="Flow")
    await flow.first.wait_for(timeout=15_000)
    await flow.first.click()
    await page.wait_for_url("**/flow", timeout=10_000)
    return "/flow" in page.url


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()

    pass_flow = _pass_flow()
    edges = await flow_service.list_edges()
    edges.append(
        EdgeListItem(
            edge_id="edge-pass",
            hypothesis=pass_flow.hypothesis,
            frozen=True,
            stage=furthest(pass_flow.stages),
        )
    )
    flow = await flow_service.load_flow("edge-001")
    stages = stage_defs()
    templates = flow_templates.templates()
    print("\n── Real flow data (elgar journal → flow_service)")
    _record(
        "edge-001 present + frozen",
        any(e.edge_id == "edge-001" and e.frozen for e in edges),
    )
    _record("edge-001 flow has 9 stages", flow is not None and len(flow.stages) == 9)

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    await page.route(
        "**/api/v1/iam/me",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=json.dumps(FAKE_USER)
        ),
    )
    await page.route(
        "**/api/v1/health/boot/sync-stream",
        lambda r: r.fulfill(status=200, content_type="text/event-stream", body=""),
    )
    await page.route(
        "**/api/v1/health/boot",
        lambda r: r.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"services": []}),
        ),
    )
    await page.route(
        "**/api/v1/flow/edges/edge-001",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=flow.model_dump_json()
        ),
    )
    await page.route(
        "**/api/v1/flow/edges",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=_dump(edges)
        ),
    )
    await page.route(
        "**/api/v1/flow/stages",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=_dump(stages)
        ),
    )
    await page.route(
        "**/api/v1/flow/templates",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=_dump(templates)
        ),
    )
    run_done = _done_run()
    await page.route(
        "**/api/v1/flow/edges/edge-001/run",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=run_done.model_dump_json()
        ),
    )
    await page.route(
        "**/api/v1/flow/edges/edge-pass",
        lambda r: r.fulfill(
            status=200,
            content_type="application/json",
            body=pass_flow.model_dump_json(),
        ),
    )
    sizing = flow_sizing.size(SizingInputs(capital=1_000_000, adv_inr=5_000_000))
    await page.route(
        "**/api/v1/flow/sizing",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=sizing.model_dump_json()
        ),
    )
    redteam = _redteam_done()
    await page.route(
        "**/api/v1/flow/edges/edge-pass/redteam",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=redteam.model_dump_json()
        ),
    )
    approve = _approve_state()
    await page.route(
        "**/api/v1/flow/edges/edge-pass/approve",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=approve.model_dump_json()
        ),
    )
    plan = flow_live.build_plan("edge-pass", "a survivor", 62_500.0)
    await page.route(
        "**/api/v1/flow/edges/edge-pass/live",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=plan.model_dump_json()
        ),
    )
    await page.route(
        "**/api/v1/flow/edges/edge-pass/reconcile",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=_recon_hard().model_dump_json()
        ),
    )
    watch = _watch_decayed()
    await page.route(
        "**/api/v1/flow/edges/edge-pass/watch",
        lambda r: r.fulfill(
            status=200, content_type="application/json", body=watch.model_dump_json()
        ),
    )

    try:
        print("\n── Auth + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached /flow (not /login)", on_app, page.url)
        if not on_app:
            return False
        await page.wait_for_selector("[data-flow-rail]", timeout=15_000)

        print("\n── The locked 9-stage rail (real status)")
        nodes = await page.locator("[data-stage]").count()
        _record("All 9 stages render", nodes == 9, f"{nodes} nodes")
        _record(
            "edge-001 frozen chip",
            await page.locator('[data-edge="edge-001"] .of-chip').count() >= 1,
        )
        test_state = await page.locator('[data-stage="test"]').get_attribute(
            "data-state"
        )
        _record("Test stage DONE (ran)", test_state == "done", str(test_state))

        print("\n── Test stage — the funnel run (gates)")
        await page.locator('[data-stage="test"]').click()
        await page.wait_for_selector("[data-run-funnel]", timeout=8_000)
        gates = await page.locator("[data-test-run] [data-gate]").count()
        _record("Test renders the 4 funnel gates", gates == 4, f"{gates} gates")
        g1 = await page.locator('[data-gate="1"]').get_attribute("class")
        _record("Gate-1 shows FAILED (the killer)", "g-failed" in (g1 or ""))
        body = await page.evaluate("() => document.body.innerText")
        _record("Test verdict shows FAIL", "FAIL" in body)
        await page.screenshot(path=str(SHOT_DIR / "flow-01-test.png"))

        print("\n── Range stage — the downside-first cone")
        await page.locator('[data-stage="range"]').click()
        await page.wait_for_selector("[data-range-cone]", timeout=8_000)
        es = await page.locator("[data-es]").inner_text()
        _record(
            "Range cone leads with the worst-case ES P5", es.strip().startswith("−"), es
        )
        await page.screenshot(path=str(SHOT_DIR / "flow-02-range.png"))

        print("\n── Plan stage — deterministic sizing (surviving edge)")
        await page.locator('[data-edge="edge-pass"]').click()
        await page.wait_for_selector(
            '[data-stage="plan"][data-state="active"]', timeout=8_000
        )
        await page.locator('[data-stage="plan"]').click()
        await page.wait_for_selector("[data-plan-sizing]", timeout=8_000)
        cons = await page.locator("[data-constraint]").count()
        _record("Plan shows the sizing constraints", cons >= 3, f"{cons} constraints")
        _record(
            "Recommended position renders",
            await page.locator("[data-recommended]").count() >= 1,
        )
        _record(
            "The binding constraint is highlighted",
            await page.locator("[data-constraint].binding").count() == 1,
        )
        await page.screenshot(path=str(SHOT_DIR / "flow-03-plan.png"))

        print("\n── Red-team stage — the only LLM stage (cage-metered)")
        await page.locator('[data-stage="redteam"]').click()
        await page.wait_for_selector("[data-redteam]", timeout=8_000)
        objs = await page.locator("[data-objection]").count()
        _record("Red-team renders severity-tagged objections", objs >= 2, f"{objs} objections")
        _record("High-severity objection leads",
                await page.locator('[data-objection="high"]').count() >= 1)
        _record("10th-Man dissent renders", await page.locator("[data-tenth-man]").count() >= 1)
        _record("Metering attribution shown (cage)", await page.locator("[data-meter]").count() >= 1)
        await page.screenshot(path=str(SHOT_DIR / "flow-04-redteam.png"))

        print("\n── Approve stage — downside-first, ack-loss-first")
        await page.locator('[data-stage="approve"]').click()
        await page.wait_for_selector("[data-approve-panel]", timeout=8_000)
        _record("Approve leads with the worst-case loss", await page.locator("[data-downside]").count() >= 1)
        _record("Approve is DISABLED before acknowledging the loss",
                await page.locator("[data-approve]").is_disabled())
        await page.locator("[data-ack] input").check()
        _record("Acknowledging the loss ENABLES Approve",
                not await page.locator("[data-approve]").is_disabled())
        await page.screenshot(path=str(SHOT_DIR / "flow-05-approve.png"))

        print("\n── Live stage — prepare orders + reconcile (never auto-executes)")
        await page.locator('[data-stage="live"]').click()
        await page.wait_for_selector("[data-live-panel]", timeout=8_000)
        _record("Live shows the never-auto-execute banner", await page.locator("[data-noauto]").count() >= 1)
        _record("Live prepares the order plan (entry + guards)",
                await page.locator("[data-order]").count() >= 3)
        await page.locator("[data-reconcile-form] input").nth(0).fill("X")
        await page.locator("[data-reconcile-form] input").nth(1).fill("100")
        await page.locator("[data-reconcile-form] input").nth(2).fill("1000")
        await page.locator("[data-reconcile-form] input").nth(3).fill("790")
        await page.locator("[data-reconcile]").click()
        await page.wait_for_selector('[data-recon-out][data-guard="hard"]', timeout=8_000)
        _record("Reconcile lights the HARD guard on a -21% read-back", True)
        await page.screenshot(path=str(SHOT_DIR / "flow-06-live.png"))

        print("\n── Watch stage — decay monitor + decay-kill")
        await page.locator('[data-stage="watch"]').click()
        await page.wait_for_selector("[data-watch-panel]", timeout=8_000)
        await page.locator("[data-watch-panel] input").first.fill("-5")
        await page.locator("[data-add-period]").click()
        await page.wait_for_selector('[data-watch-out][data-verdict="decayed"]', timeout=8_000)
        _record("Watch flags the edge DECAYED", True)
        _record("Decay signals render", await page.locator("[data-decay]").count() >= 1)
        _record("Decay-kill is offered on a decayed edge",
                await page.locator("[data-kill-block]").count() >= 1)
        await page.screenshot(path=str(SHOT_DIR / "flow-07-watch.png"))

        print("\n── New edge → Idea/Rule authoring")
        await page.locator("[data-new-edge]").click()
        await page.wait_for_selector("[data-idea-templates]", timeout=8_000)
        fams = await page.locator("[data-template]").count()
        _record("Family A/B/C templates render", fams == 3, f"{fams} templates")
        _record(
            "Family C scaffolded (disabled)",
            await page.locator('[data-template="tpl-c-event-driven"]').is_disabled(),
        )
        _record(
            "Rule author form present",
            await page.locator("[data-edge-author]").count() >= 1,
        )
        await page.screenshot(path=str(SHOT_DIR / "flow-02-author.png"))

    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--cdp-port", type=int, default=DEFAULT_CDP)
    args = parser.parse_args()

    print(f"Flow Cockpit UI Probe (real data)  →  {args.base}  [CDP :{args.cdp_port}]")
    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
