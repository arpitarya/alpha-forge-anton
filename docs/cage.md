# Cage cost ledger (Orff integration)

**Cage** is the sibling *flux* (`~/my_programs/cage`, `git@github.com:arpitarya/cage.git`):
a deterministic, `$0`, stdlib-only attribution ledger for LLM token traffic. It
meters every call, collects a savings receipt from each tool in the stack, and
derives spend / per-tool attribution / counterfactuals. Design of record:
`cage/docs/cage-plan.md` (canonical — no longer mirrored in this repo).

Cage is the fourth deterministic substrate tool beside graphify (code→graph), fux
(decisions→rules/memory), and elgar (private money docs).

## How Anton meters

The Orff gateway is Cage's first integration point. Every completion is recorded
where its cost is already known (cage-plan §5):

| Piece | Where |
| ----- | ----- |
| Adapter (fail-open) | [concierge/llm/.../cage_meter.py](../concierge/llm/src/alphaforge_anton_llm/cage_meter.py) |
| Wiring | [LLMGateway.complete](../concierge/llm/src/alphaforge_anton_llm/gateway.py) → `cage_meter.record(resp, …)` on each success |
| Ledger + policy | `.cage/policy.toml` (committed) · `.cage/ledger/` (gitignored) |

`cage_meter.record` builds one call row from the `ProviderResponse` — `route =
QueryType.value`, `agent = "orff"`, cost from `pricing.estimate_cost_usd` (Anton's
authoritative price table). It is **fail-open**: if cage isn't installed or anything
raises, metering is a silent no-op, so it can never break a completion.

**Runtime critic (`runtime-note-pii`).** The deterministic money/PII block in
`critic_guard` is **`$0`** — pure in-process regex, no LLM, nothing to meter. Its
**advisory** judgment layer (`fux critic`) only spends tokens if a host-agent
self-critique actually runs through the LLM gateway, and that completion is metered
here like any other (`agent = "orff"`). So the guard adds metered spend only when it
genuinely asks the model for a judgment — the block path stays free.

## Enabling it

Cage is an optional dependency (`[cage]` extra, a uv path source):

```bash
cd concierge/llm && uv sync --extra cage     # or: uv pip install -e ../../../cage
```

Without the extra the gateway still runs — metering just no-ops.

## Reading the ledger

From the Anton repo root (so `.cage/policy.toml` is picked up):

```bash
cage report --by route          # spend by Orff intent (query_type)
cage report --by model          # spend by model
cage attrib --task <id>         # per-tool marginal savings (graphify, fux, …)
cage why <call-id>              # full provenance: a call + its receipts
cage budget --session <id>      # spend vs the policy ceilings (subsumes CostGuard)
```

Tools in Anton's stack (graphify, fux, the Handover compressor, the response
cache) file **savings receipts** via `cage.record_receipt(...)` so `cage attrib`
can credit each one — that is the part that turns a meter into attribution.

## PII / secrets

The ledger stores token **counts** and cost — never prompt bodies or holdings, by
construction (cage-plan §10). For production, point `CAGE_LEDGER` at the private
**elgar** store so even the counts live outside this repo:

```bash
export CAGE_LEDGER="$HOME/.alphaforge-anton/elgar/cage-ledger"
```

## Dev surface (Claude Code / Codex in this repo)

Beyond the runtime Orff integration, Cage is wired into the agents used to *develop*
Anton so their token spend is metered too:

```bash
cage hooks install --claude --codex   # SessionEnd transcript metering + cage MCP
```

This adds a `SessionEnd` hook (records each Claude Code session's transcript) and
the `cage` MCP read server to `.mcp.json`, so you can ask "what did this session
cost?" from inside the editor. See `cage/docs/agents.md` for all four agents.

## Verification

- Adapter unit test: [concierge/llm/tests/test_cage_meter.py](../concierge/llm/tests/test_cage_meter.py)
  (`uv run --extra cage pytest tests/test_cage_meter.py`).
- Cage's own suite (48 passing) and `cage demo` reproduce the plan's §4.4 tables.
