/** Watch-stage view-models — hand-mirrored from `app/modules/flow/flow_watch_schema.py`.
 *  Deterministic decay monitor; the decay-kill journals a retirement to elgar. */

export type DecaySeverity = "high" | "med" | "low";
export type WatchVerdict = "healthy" | "decaying" | "decayed";

export interface Observation {
  period: string;
  return_pct: number;
}

export interface DecaySignal {
  severity: DecaySeverity;
  name: string;
  detail: string;
}

export interface WatchState {
  n_periods: number;
  realized_expectancy: number;
  hit_rate: number;
  max_dd: number;
  expected_expectancy: number;
  signals: DecaySignal[];
  verdict: WatchVerdict;
  kill_recommended: boolean;
}

export interface RetirementRecord {
  edge_id: string;
  reason: string;
  realized_expectancy: number;
  max_dd: number;
  retired_at: string;
  ref: string | null;
}
