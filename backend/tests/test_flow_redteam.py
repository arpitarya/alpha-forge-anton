"""Red-team — the only LLM stage: JSON parse, severity sort, repair round, cache + gating.

The LLM is MOCKED (no spend, deterministic): we assert the service parses the model's JSON
into a severity-sorted `RedteamReport`, runs one repair round on bad JSON then succeeds,
caches per edge (no re-bill), and that Red-team is OFF the deterministic path — its module
never imports the funnel/sizing engines. Determinism boundary: numbers come from the
context, never recomputed by the service.

    uv run pytest tests/test_flow_redteam.py -v
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from app.modules.flow import flow_redteam
from app.modules.flow.flow_redteam_schema import RedteamContext, Severity
from app.modules.flow.flow_run_schema import RunPhase

_GOOD = (
    '```json\n{"objections": [{"severity": "low", "title": "costs"}, '
    '{"severity": "high", "title": "overfit"}], "tenth_man": "regime change", '
    '"runner_ups": ["wait"], "tripwires": ["NIFTY < 200DMA"]}\n```'
)


class _Resp:
    def __init__(self, content: str) -> None:
        self.content, self.provider, self.model = content, "claude-sdk", "claude-opus-4-8"


def test_parse_sorts_by_severity_high_first():
    r = flow_redteam._parse(_GOOD, "claude-sdk", "claude-opus-4-8")
    assert [o.severity for o in r.objections] == [Severity.HIGH, Severity.LOW]
    assert r.tenth_man == "regime change" and r.tripwires == ["NIFTY < 200DMA"]
    assert r.phase == RunPhase.DONE and r.provider == "claude-sdk"


@pytest.mark.asyncio
async def test_repair_round_recovers_from_bad_json(monkeypatch):
    calls = {"n": 0}

    async def _complete(messages, **kw):
        calls["n"] += 1
        return _Resp("not json" if calls["n"] == 1 else _GOOD)

    monkeypatch.setattr(flow_redteam._gateway, "complete", _complete)
    rep = await flow_redteam._complete(flow_redteam.build_messages(RedteamContext(edge_id="e")))
    assert calls["n"] == 2 and rep.phase == RunPhase.DONE  # one repair round, then success


@pytest.mark.asyncio
async def test_start_caches_and_no_double_run(monkeypatch):
    async def _complete(messages, **kw):
        await asyncio.sleep(0)
        return _Resp(_GOOD)

    monkeypatch.setattr(flow_redteam._gateway, "complete", _complete)
    flow_redteam._CACHE.clear()
    ctx = RedteamContext(edge_id="edge-x", verdict="pass")
    first = flow_redteam.start(ctx)
    assert first.phase == RunPhase.QUEUED
    assert flow_redteam.start(ctx) is flow_redteam.get("edge-x")  # in-flight → same cached object
    await asyncio.sleep(0.05)
    assert flow_redteam.get("edge-x").phase == RunPhase.DONE


def test_redteam_is_off_the_deterministic_path():
    # the LLM stage must not IMPORT the funnel/sizing engines (numbers in, never recomputed)
    imports = [
        ln for ln in Path(flow_redteam.__file__).read_text().splitlines()
        if ln.startswith(("import ", "from "))
    ]
    joined = "\n".join(imports)
    assert "funnel" not in joined and "flow_sizing" not in joined and "factor_" not in joined
