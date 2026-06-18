"""Concierge tool-calling probe — standalone, no CDP, no live LLM.

Registry shape, executor dispatch, confirm-card purity,
tool-layer non-trusted no-op, Anthropic mock loop.
Run: just probe concierge-tools
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:  # noqa: C901
    from app.modules.concierge.tool_registry import (
        DEEP_SEARCH_TOOL, MUTATING_TOOLS, READ_TOOLS, TOOL_SCHEMAS, trusted_schemas,
    )
    check("13 tools declared", len(TOOL_SCHEMAS) == 13)
    check("7 read + 5 mutating + 1 deep-search", len(READ_TOOLS) == 7 and len(MUTATING_TOOLS) == 5)
    check("read ∩ mutating = ∅", READ_TOOLS.isdisjoint(MUTATING_TOOLS))
    check("deep-search is its own class", DEEP_SEARCH_TOOL not in READ_TOOLS | MUTATING_TOOLS)
    check("all fields non-empty", all(t.name and t.description and t.parameters for t in TOOL_SCHEMAS))
    check("trusted_schemas() = all 13", len(trusted_schemas()) == 13)
    check("Never drops deep-search", len(trusted_schemas(offer_deep_search=False)) == 12)

    from app.modules.concierge.tool_executor import build_confirm, execute_read
    card = build_confirm("edit_exclusion_list", {"symbol": "SPICEJET", "action": "add"})
    check("exclusion card fields", all(f in card for f in ("id", "action", "summary", "steps", "apply")))
    check("exclusion apply.path", card["apply"]["path"] == "/api/v1/concierge/exclusion")
    check("exclusion apply.body has 'add'", "add" in card["apply"]["body"])
    check("objective apply.path", build_confirm("set_objective", {"monthly_target_inr": 12000})["apply"]["path"] == "/api/v1/signals/objective")
    check("context apply.path → /memory/append", build_confirm("update_context", {"note": "x"})["apply"]["path"] == "/api/v1/concierge/memory/append")
    with patch("app.modules.plans.elgar_bridge.save") as ms:
        build_confirm("edit_exclusion_list", {"symbol": "X", "action": "remove"})
        check("build_confirm is pure — no elgar write", not ms.called)

    fake_cfg = MagicMock(); fake_cfg.model_dump.return_value = {"universe": ["HDFC"]}
    with patch("app.modules.signals.strategy_config.load_config", return_value=fake_cfg):
        result = asyncio.run(execute_read("get_strategy", {}))
    check("execute_read(get_strategy) → dict", isinstance(result, dict) and "universe" in result)
    try:
        asyncio.run(execute_read("nonexistent", {})); check("unknown tool raises", False)
    except ValueError:
        check("unknown tool raises ValueError", True)

    from app.modules.concierge.tool_layer import run
    a0 = MagicMock(); a0.preferred = "gemini"; a0.confirmed = True
    evts, resp = asyncio.run(run(a0, None))
    check("non-trusted → ([], None)", evts == [] and resp is None)

    # Compact fake Anthropic response classes
    class _U: input_tokens = 10; output_tokens = 5
    class _RTb: type = "tool_use"; id = "t1"; name = "get_strategy"; input = {}
    class _MTb: type = "tool_use"; id = "t2"; name = "edit_exclusion_list"; input = {"symbol": "SPICEJET", "action": "add"}
    class _FT: type = "text"; text = "Done."
    class _R1: content = [_RTb()]; usage = _U()
    class _R2: content = [_FT()]; usage = _U()
    class _M1: content = [_MTb()]; usage = _U()

    a1 = MagicMock(); a1.preferred = "claude-sdk"; a1.confirmed = True; a1.msgs = []; a1.model = "m"
    mc1 = MagicMock(); mc1.messages.create = AsyncMock(side_effect=[_R1(), _R2()])
    with patch("anthropic.AsyncAnthropic", return_value=mc1), \
         patch("app.modules.signals.strategy_config.load_config", return_value=fake_cfg), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "k"}):
        evts1, resp1 = asyncio.run(run(a1, None))
    check("read tool → tool event in stream", any("tool" in e for e in evts1))
    check("read tool → final ProviderResponse", resp1 is not None and "Done." in resp1.content)

    a2 = MagicMock(); a2.preferred = "claude-sdk"; a2.confirmed = True; a2.msgs = []; a2.model = "m"
    mc2 = MagicMock(); mc2.messages.create = AsyncMock(return_value=_M1())
    with patch("anthropic.AsyncAnthropic", return_value=mc2), \
         patch("app.modules.plans.elgar_bridge.save") as ms2, \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "k"}):
        evts2, _ = asyncio.run(run(a2, None))
    check("mutating tool → confirm event", any("confirm" in e for e in evts2))
    check("no elgar write from tool loop", not ms2.called)

    print("\n" + ("❌ concierge-tools probe FAILED" if _fail else "✅ Tool registry, executor & layer guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
