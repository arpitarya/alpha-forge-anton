"""Tool registry — single source of truth for all Orff tool schemas.

Names + schemas authored once; Python uses them for the tool loop,
the frontend uses them for ToolTrail rendering.
See docs/orff-tool-calling.handoff.md.
"""
from __future__ import annotations

from alphaforge_anton_llm.types import ToolSchema

_S = ToolSchema  # compact alias

TOOL_SCHEMAS: list[ToolSchema] = [
    # ── Read tools (auto-run, no confirmation) ───────────────────────────────
    _S(name="get_plan",
       description="Load the active allocation plan (targets by asset class).",
       parameters={"type": "object", "properties": {
           "plan_id": {"type": "string", "description": "plan id, default core-allocation"}}}),
    _S(name="get_drift",
       description="Per-class actual-vs-plan drift in percentage points.",
       parameters={"type": "object", "properties": {
           "plan_id": {"type": "string", "description": "plan id, default core-allocation"}}}),
    _S(name="review_holdings",
       description="Deterministic buy/hold/trim/sell ActionPlan over current holdings.",
       parameters={"type": "object", "properties": {}}),
    _S(name="screen_candidates",
       description="Ranked new-entry candidates filtered by the active strategy.",
       parameters={"type": "object", "properties": {
           "theme": {"type": "string", "description": "optional sector/theme filter"},
           "limit": {"type": "integer", "description": "max results, default from config"}}}),
    _S(name="get_strategy",
       description="Active strategy config — trim rule, stop-loss, min-score knobs.",
       parameters={"type": "object", "properties": {}}),
    _S(name="latest_action_plan",
       description="Last saved ActionPlan from the elgar ledger + diff vs current holdings.",
       parameters={"type": "object", "properties": {}}),
    _S(name="get_objective",
       description="North-star objective: monthly target, horizon, risk, mission, active_target.",
       parameters={"type": "object", "properties": {}}),
    # ── Mutating tools (ApprovalCard confirm flow — never silent writes) ──────
    _S(name="set_strategy_knob",
       description="Propose a strategy-config change (e.g. trim_rule.mode). Emits ApprovalCard.",
       parameters={"type": "object",
                   "properties": {
                       "knob": {"type": "string", "description": "dotted path, e.g. trim_rule.mode"},
                       "value": {"description": "new value (string, number, or boolean)"}},
                   "required": ["knob", "value"]}),
    _S(name="edit_exclusion_list",
       description="Add or remove a stock from the never-buy list. Emits ApprovalCard.",
       parameters={"type": "object",
                   "properties": {
                       "symbol": {"type": "string", "description": "NSE ticker, e.g. SPICEJET"},
                       "action": {"type": "string", "enum": ["add", "remove"]}},
                   "required": ["symbol", "action"]}),
    _S(name="update_context",
       description="Append a note to the standing Orff context doc. Emits ApprovalCard.",
       parameters={"type": "object",
                   "properties": {
                       "note": {"type": "string", "description": "text to append"}},
                   "required": ["note"]}),
    _S(name="save_action_plan",
       description="Persist the current ActionPlan to the elgar ledger. Emits ApprovalCard.",
       parameters={"type": "object", "properties": {}}),
    _S(name="set_objective",
       description="Update the monthly P&L target, horizon, or mission. Emits ApprovalCard.",
       parameters={"type": "object", "properties": {
           "monthly_target_inr": {"type": "number"},
           "horizon": {"type": "string", "enum": ["swing", "long_term"]},
           "risk_tolerance": {"type": "string",
                              "enum": ["conservative", "moderate", "aggressive"]},
           "mission": {"type": "string"}}}),
    # ── Spend tool (confirm-gated, its own class — writes nothing) ────────────
    _S(name="request_deep_search",
       description=(
           "Request a paid Parallel web search when you lack current data to answer "
           "accurately (live prices, news, events past your knowledge cutoff). Give concrete "
           "reasons and the exact queries. Confirm-gated — no spend until the user approves. "
           "Prefer this over guessing or answering from stale knowledge."),
       parameters={"type": "object",
                   "properties": {
                       "reasons": {"type": "string",
                                   "description": "why fresh web data is needed (user-facing)"},
                       "queries": {"type": "array", "items": {"type": "string"},
                                   "description": "exact search queries to run"}},
                   "required": ["reasons", "queries"]}),
]

# Slices match the declaration order: first 7 reads, next 5 mutating, last is the spend tool.
READ_TOOLS: frozenset[str] = frozenset(t.name for t in TOOL_SCHEMAS[:7])
MUTATING_TOOLS: frozenset[str] = frozenset(t.name for t in TOOL_SCHEMAS[7:12])
DEEP_SEARCH_TOOL = "request_deep_search"


def trusted_schemas(*, offer_deep_search: bool = True) -> list[ToolSchema]:
    """Schemas for the trusted claude-sdk lane (non-trusted gets nothing);
    request_deep_search is dropped when deep_search_mode is Never."""
    if offer_deep_search:
        return list(TOOL_SCHEMAS)
    return [t for t in TOOL_SCHEMAS if t.name != DEEP_SEARCH_TOOL]
