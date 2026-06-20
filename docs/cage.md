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

## Savings sources Anton feeds

Two non-LLM savings axes are populated so `cage human` / `cage trend` / `cage
matrix` produce numbers (both off the request path, both fail-open with cage
absent):

| Source | What feeds it | Where |
| ------ | ------------- | ----- |
| **Human alternatives** (Tier-1, agent-vs-human) | one `tool="human"` receipt per task at task close | [cage_human.py](../concierge/llm/src/alphaforge_anton_llm/cage_human.py) |
| **graphify token savings** | one `tool="graphify"` `modeled` receipt per metered query | [bin/graphify](../bin/graphify) shim → `cage graphify` |

**Human alternatives.** `cage_human.backfill` walks `tasks.jsonl` (written first by
`cage hook-session-end`) and calls `cage.record_human(task=<id>, task_type=<type>)`
for each task — Anton supplies only the id and type; cage's resolver + the
`[human.tasks.*]` policy table do minutes→USD and the confidence ladder. A typeless
task falls to cage's global default (honestly low-confidence) — **no minutes are
invented**. `record_human` is idempotent on `(task, call)`, so re-running never
double-records. Wired as a **second `SessionEnd` step after** `cage hook-session-end`
(in `.claude/settings.json`), and runnable as `just cage-human`. Feeds `cage human`
and `cage trend` (the $ **and** hours-saved time-series).

**graphify metering.** graphify is third-party and read-only, so cage meters it by
wrapping the unmodified command: `cage graphify -- graphify query "…"`. The
`bin/graphify` shim routes every bare `graphify query/path/explain` through that
wrapper transparently — stdout/exit pass through unchanged, and a `tool="graphify"`,
`method="modeled"` receipt is filed on the side (or nothing, when no cited
`source_file` resolves — unmeasurable ≠ zero). `graphify update .` stays unwrapped
(a refresh, not a query). Also `just graphify-cage 'query "…"'`. Verified by
`just probe graphify-cage`.

The shim + PATH wiring is **not hand-maintained here** — it's installed by the
PyPI-packaged **`cage adopt`** command (no repo to clone): `cage adopt` runs
`cage init`, `cage hooks install`, and drops the graphify interceptor (which ships
*inside* the `cage-flux` wheel as `data/shims/graphify`) + the PATH line.
`setup.sh --graphify` calls `cage adopt --no-hooks` (anton wires its own SessionEnd
above). Re-run `setup.sh --graphify`, or `cage adopt --no-hooks` directly, to
reinstall the shim.

> **Version note.** These surfaces need **cage ≥ 0.3** (`graphify` / `human-record`
> subcommands, `record_human`). Install/upgrade the tool with
> `uv tool install cage-flux` (or `pip install cage-flux`); anton's `[cage]`
> extra pins `cage-flux==0.3.0` for the in-process `cage_meter` / `cage_human`
> adapters. The shim uses the global `cage` and no-ops cleanly if it's absent.

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
