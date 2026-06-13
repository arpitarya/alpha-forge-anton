"""Holdings-disclosure probe — proves Orff answers holdings questions without leaking.

Standalone (no CDP, no LLM call). Asserts the two guarantees from the Fux
`secure-holdings-plan` entry:
  1. disclosed_context() renders PERCENTAGES ONLY — never ₹ or symbols, even when the
     portfolio is populated.
  2. A private (holdings) query routes ONLY to a trusted provider — a free-provider pin
     is overridden, never honoured.

Run:  just probe holdings-disclosure
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "probes"))

from plan_safety_probe import scan_text  # reuse the data-plane leak patterns

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    from alphaforge_anton_llm import registry
    from alphaforge_anton_llm.types import QueryType

    from app.modules.plans.plan_drift import ClassDrift
    from app.modules.plans.plan_loader import Plan
    from app.modules.concierge import holdings_detail as hd
    from app.modules.concierge import holdings_private as hp

    # 1. disclosure renders clean even with a *populated* portfolio
    fake_plan = Plan("test", "long-term", {}, {}, [])
    fake_rows = [
        ClassDrift("equity", 60, 67, 7.0, 5.0, "hot", "trim ~7pts"),
        ClassDrift("bond", 15, 9, -6.0, 5.0, "cold", "add ~6pts"),
        ClassDrift("cash", 2, 2, 0.0, 5.0, "ok", ""),
    ]
    hp.drift_for_plan = lambda plan_id="core-allocation": (fake_plan, fake_rows)
    leaks = scan_text(hp.disclosed_context())
    check("disclosed_context is percentages-only (no ₹/symbols)", not leaks, f"leaked {leaks}")
    check("leak guard is armed", bool(scan_text("equity RELIANCE worth ₹1,23,456")))

    # 1b. missing elgar plan → actuals-only fallback, never an exception (the
    #     "fetch the holdings" → Failed-to-fetch regression), still percentages-only
    def _no_plan(plan_id: str = "core-allocation"):
        raise FileNotFoundError("no plan in elgar store")

    class _Slice:
        class asset_class:
            value = "equity"
        pct = 61.5

    class _StubAgg:
        def allocation(self):
            return [_Slice()]

    hp.drift_for_plan = _no_plan
    hd.HoldingsAggregator = _StubAgg
    try:
        ctx = hp.disclosed_context()
        check("missing plan degrades instead of raising", True)
    except Exception as exc:  # noqa: BLE001
        ctx = ""
        check("missing plan degrades instead of raising", False, f"{type(exc).__name__}: {exc}")
    check("fallback is percentages-only (no ₹/symbols)", not scan_text(ctx), f"leaked {scan_text(ctx)}")
    check("fallback forbids inventing targets", "do NOT invent targets" in ctx)
    check("fallback discloses actual class mix", "equity: 62%" in ctx, ctx[:120])

    # 1c. full rows flow ONLY to the trusted lane (detailed_context chokepoint)
    fake_row = (
        "- [zerodha] RELIANCE · equity: qty 50 @ avg 2,410.00, ltp 2,891.00 → "
        "now ₹144,550, P&L +19.9%, day +0.4%"
    )
    hp.holdings_table = lambda max_rows=60: fake_row
    detail = hp.detailed_context("claude-sdk")
    check("trusted provider receives actual holding rows", "RELIANCE" in detail, detail[:120])
    check("trusted detail flags itself as authorized", "FULL DETAIL" in detail)
    check("trusted detail still surfaces the missing plan", "elgar save" in detail)
    for untrusted in ("gemini", None):
        ctx = hp.detailed_context(untrusted)
        clean = "RELIANCE" not in ctx and not scan_text(ctx)
        check(f"untrusted ({untrusted}) gets percentages-only, no symbols", clean, ctx[:120])

    # 2. a private query floors to a trusted provider for every selectable provider
    trusted = registry.trusted_providers()
    for prov in ["auto", "gemini", "groq", "claude-sdk", "openrouter"]:
        _, preferred, _, _ = hp.enforce_floor(prov, QueryType.PORTFOLIO_PRIVATE)
        check(f"private + {prov:11}→ trusted provider ({preferred})", preferred in trusted)
    _, pref, _, _ = hp.enforce_floor("gemini", QueryType.NEWS_LOOKUP)
    check("non-private keeps the user's provider", pref == "gemini")

    # 3. holdings text classifies private and its whole chain is trusted
    qt = registry.classify_intent("how is my portfolio allocation drifting")
    chain = set(registry.chains().get("portfolio_private", []))
    check("holdings query classified private", registry.is_private(qt))
    check("portfolio_private chain ⊆ trusted", bool(chain) and chain <= trusted, f"chain={chain}")

    print("\n" + ("❌ disclosure probe FAILED" if _fail else "✅ disclosure guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
