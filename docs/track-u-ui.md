# Track U — integrated Hi-Fi UI (mock + honest-pending)

Track U builds the integrated **Alpha Forge Hi-Fi** as real, probe-verified React
components on **MOCK + honest-pending** data. It does **not** block the engine track
and wires to real data only in Phase 3. The data shapes are the Phase-0 contracts
(`frontend/src/modules/contracts/*` — `Objective`, `Cone`, `ApprovalProposal`,
`DecisionRow`, `FeedState`, `Calibration`), imported directly, never re-declared.

**Visual source of truth:** the claude.ai/design project `Alpha Forge` (`f8c530b3-…`),
files `int-context.jsx` / `int-app.jsx` / `forge-redline.css`. The `.of-*` styles are
ported into `frontend/src/app/forge-*.css` minus the prototype's `.of-root` token block —
they inherit anton's existing theme tokens, so there are **no new color tokens and no
hardcoded hex**. Space Grotesk / Space Mono only; no gauges/dials; **React state only,
no localStorage**; honest-pending is dashed/striped, never a faked 0%; never auto-execute.

## Surfaces

| Surface | Route / mount | Components |
|---|---|---|
| **Goals** (editable north-star) | `/goals` | `modules/goals/` — `GoalsPanel` (Calmar hero target 3 / floor 2 · −12/−20 drawdown guard · edges pending · self-funding "not yet covered" · capital-structure bar in a collapsed `<details>`), `GoalsScore`, `GoalsStructure`, `GoalsAside` (capital tiles + proposal-log preview → Decisions). Edits route into chat (`Propose change →`), never a silent write. |
| **Decisions** (replayable ledger) | `/decisions` | `modules/decisions/` — `DecisionsLedger`, `CalibrationSummary` (13 cleared · 4 stop · 3 open — the figures the approval chip references), `DecisionRowCard` (proposal → downside-shown → decision → outcome `cleared_cone`/`hit_stop`/`open` + REPLAY gated on `replayable`). |
| **Orff conversation** (live surface) | `ChatRail` thread | `modules/concierge/` — `GuardrailStrip` (pinned READ-ONLY: aim · Calmar · drawdown · "edit in Goals →"), `GroundedAnswer` (fresh / stale / error), `ConeCard` (P5–P95 fan, bold red ES, low-confidence fuzzed), `ProposalCard` (downside-first ES hero, tap-to-ack gates Approve, calibration chip, balanced reasoning with 10th-Man/runner-ups/tripwires collapsed, binary Approve/Veto, cooldown, exec checklist), `FeedToggle` (LIVE/STALE/ERROR). |
| **Nav** | `TerminalTopBar` | Additive: Terminal · Portfolio · **Goals** · **Decisions**. Terminal stays the landing page; Portfolio & Terminal untouched. (Wireframe intentionally omitted.) |

Shared primitives live in `modules/forge/` (`Num`, `UChip`, `FanChart` + `fan.utils`,
`Www`). The existing `concierge/ObjectivePanel.tsx` (old `signals/objective` shape) and
its `ui-objective` probe are left untouched — Goals is the new Phase-0 surface.

## The LIVE/STALE/ERROR feed contract

`FeedToggle` drives the honest-pending story on the inline proposal:
- **STALE** — the cone refuses to re-price ("₹0 because the feed hasn't refreshed —
  not because you're flat") and `ProposalCard` Approve is blocked even after the loss
  is acknowledged.
- **ERROR** — the forecast is withheld entirely (cone + proposal not shown); a red
  grounding-error badge explains why. An error is never a fabricated answer.
- **LIVE** — normal; the cone re-prices and Approve unlocks once the ES loss is tapped.

## The `/proposal` demo trigger

The inline cone + proposal are MOCK-only and client-driven: the `/proposal` slash
command (and an EmptyState seed chip) renders `ProposalDemo` in the thread — no API,
no backend. `proposal.mock.ts` holds the `ApprovalProposal` + execution orders + sources.

## Verification

CDP probes (`:9299`, never Playwright-MCP) — run via `just probe <name>`:

| Probe | Asserts |
|---|---|
| `just probe ui-goals` | Calmar hero + −12/−20 marks; edges/structure dashed pending (not 0%); "Propose change" opens chat (no silent write) |
| `just probe ui-decisions` | ledger rows; calibration 13·4·3; REPLAY only on replayable rows + re-run summary |
| `just probe ui-proposal` | guardrail strip; `/proposal` injects the turn; red worst-case; Approve gated on the ES tap |
| `just probe ui-feedstate` | STALE freezes the cone to ₹0 + blocks Approve; LIVE restores both |

Plus `pnpm type-check && pnpm lint && pnpm build` green, and `tests/test_contracts_sync.py`
unaffected (no contract edits).
