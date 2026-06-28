// Track-U mock data for the Goals surface. The MANDATE is the Phase-0 `Objective`
// contract (imported, never re-declared); the live MEASUREMENTS (Calmar so far,
// current drawdown, validated edges) are a separate shape because they are
// observed, not declared — and Track U wires them to real data only in Phase 3.
// React state only, no API, no storage. ₹ are worked-example figures (not real
// positions) — permitted by plan-store; real figures live in elgar.
import type { Objective } from "@/modules/contracts";

/** The program mandate — exactly the Phase-0 Objective contract shape. */
export const OBJECTIVE_MOCK: Objective = {
  aim: "Grow my capital as fast as it safely can — and prove it.",
  calmar_target: 3,
  calmar_floor: 2,
  drawdown_guard: { soft: -12, hard: -20 },
  horizon: "swing",
  risk_tolerance: "aggressive",
  self_funding: {
    opex_per_month: 85000,
    cage_savings_per_month: 0,
    reserve: 200000,
    covered: false,
  },
  capital_structure: { groww: 620000, zerodha: 480000, reserve: 200000 },
};

/** Observed/measured side — honest-pending where there is not yet enough data.
 * `edges` is the LIVE (promoted-to-capital) count; `tested`/`killed`/`kill_rate`
 * are the edge-library funnel from the discovery journal (GET /edges/summary). */
export interface GoalsLive {
  /** Realised Calmar so far, or null when < 90 trading days (renders pending). */
  calmar: number | null;
  /** Current trailing drawdown %, or null when pending. */
  current_dd: number | null;
  /** Validated live edges (promoted to capital) and the target band. */
  edges: number;
  edges_target: string;
  /** Edge-library funnel — edges tested, killed, and the kill-rate (0.0–1.0). */
  tested: number;
  killed: number;
  kill_rate: number;
}

export const GOALS_LIVE_MOCK: GoalsLive = {
  calmar: 2.4,
  current_dd: -8.2,
  edges: 0,
  edges_target: "2–3",
  tested: 1,
  killed: 1,
  kill_rate: 1,
};

/** First-run variant — nothing measurable yet; everything renders dashed/pending. */
export const GOALS_LIVE_PENDING: GoalsLive = {
  calmar: null,
  current_dd: null,
  edges: 0,
  edges_target: "2–3",
  tested: 0,
  killed: 0,
  kill_rate: 0,
};
