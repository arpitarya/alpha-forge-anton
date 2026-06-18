"""Phase 4 probe — model tiering, the thinking gate, the Think-harder toggle, and the
adaptive-thinking stream split. Standalone, no API, no CDP. Run: just probe claude-tiering
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "concierge" / "llm" / "src"))
sys.path.insert(0, str(ROOT / "backend"))
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _tiers() -> None:
    from alphaforge_anton_llm import registry
    from alphaforge_anton_llm.types import QueryType as Q
    check("review/strategy → Opus 4.8",
          registry.model_for("claude-sdk", "investment_plan") == "claude-opus-4-8"
          and registry.model_for("claude-sdk", "stock_pick") == "claude-opus-4-8")
    check("chat → Sonnet 4.6 (default tier)",
          registry.model_for("claude-sdk", "factoid") == "claude-sonnet-4-6"
          and registry.model_for("claude-sdk", "multi_turn") == "claude-sonnet-4-6")
    check("classification/followup → Haiku 4.5",
          registry.model_for("claude-sdk", "followup") == "claude-haiku-4-5-20251001")
    check("effort high on review, none on chat",
          registry.effort_for("claude-sdk", "investment_plan") == "high"
          and registry.effort_for("claude-sdk", "factoid") is None)
    check("reasoning intents = plans/picks only (chat + holdings excluded)",
          registry.is_reasoning_intent(Q.INVESTMENT_PLAN)
          and registry.is_reasoning_intent(Q.STOCK_PICK)
          and not registry.is_reasoning_intent(Q.MULTI_TURN)
          and not registry.is_reasoning_intent(Q.PORTFOLIO_PRIVATE))
    check("/review classifies into the reasoning tier",
          registry.classify_intent("/review") == Q.INVESTMENT_PLAN)
    check("strategy classifies into the reasoning tier",
          registry.classify_intent("rethink the strategy") == Q.INVESTMENT_PLAN)


def _toggle() -> None:
    from alphaforge_anton_llm.types import QueryType as Q

    from app.modules.concierge.tiering_service import resolve
    check("auto + review → (opus, thinking, high)",
          resolve("auto", Q.INVESTMENT_PLAN, "claude-sdk", None) == ("claude-opus-4-8", True, "high"))
    check("auto + chat → (sonnet, no thinking)",
          resolve("auto", Q.MULTI_TURN, "claude-sdk", None) == ("claude-sonnet-4-6", False, None))
    check("Off disables thinking (model stays the intent tier)",
          resolve("off", Q.INVESTMENT_PLAN, "claude-sdk", None) == ("claude-opus-4-8", False, None))
    check("On forces thinking on chat (model stays sonnet)",
          resolve("on", Q.MULTI_TURN, "claude-sdk", None) == ("claude-sonnet-4-6", True, None))
    check("non-trusted lane passes through untouched",
          resolve("auto", Q.INVESTMENT_PLAN, "gemini", None) == (None, False, None))
    check("explicit Claude model pin respected",
          resolve("auto", Q.INVESTMENT_PLAN, "claude-sdk", "claude-opus-4-8")[0] == "claude-opus-4-8")


def _adapter() -> None:
    from alphaforge_anton_llm.providers.base import ProviderAdapter
    from alphaforge_anton_llm.providers.claude_sdk import ClaudeSdkAdapter
    from alphaforge_anton_llm.providers.groq import GroqAdapter
    check("claude adapter is reasoning-capable", ClaudeSdkAdapter.supports_reasoning is True)
    check("groq adapter is not", GroqAdapter.supports_reasoning is False)
    check("base default is False", ProviderAdapter.supports_reasoning is False)


def _stream() -> None:
    from alphaforge_anton_llm.providers._claude_stream import claude_stream

    from app.modules.concierge.stream_events import split_thinking
    ev = [
        SimpleNamespace(type="message_start", message=SimpleNamespace(usage=SimpleNamespace(input_tokens=12))),
        SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="thinking_delta", thinking="Weighing risk… ")),
        SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="thinking_delta", thinking="trim TITAN.")),
        SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="text_delta", text="Trim TITAN 5%.")),
        SimpleNamespace(type="message_delta", usage=SimpleNamespace(output_tokens=7)),
    ]

    class FS:
        def __init__(self): self._it = iter(ev)
        def __aiter__(self): return self
        async def __anext__(self):
            try:
                return next(self._it)
            except StopIteration:
                raise StopAsyncIteration
        async def __aenter__(self): return self
        async def __aexit__(self, *_): pass

    class FC:
        class messages:
            @staticmethod
            def stream(**kw): return FS()

    async def run():
        return [s async for s in claude_stream(
            client=FC(), model="claude-opus-4-8", provider_name="claude-sdk", kw={})]
    snaps = asyncio.run(run())
    thinking, visible = split_thinking(snaps[-1].content)
    check("thinking trace surfaced via <think> prefix",
          thinking == "Weighing risk… trim TITAN." and visible == "Trim TITAN 5%.")
    check("reasoning streams before the answer (a mid snapshot has thinking, no visible)",
          any(split_thinking(s.content)[0] and not split_thinking(s.content)[1] for s in snaps))


def main() -> int:
    _tiers()
    _toggle()
    _adapter()
    _stream()
    print("\n" + ("❌ claude-tiering probe FAILED" if _fail
                  else "✅ Phase-4 tiering, thinking gate, toggle & stream split hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
