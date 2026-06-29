/** Plan-stage sizing view-models — hand-mirrored from `app/modules/flow/flow_sizing_schema.py`. */

export interface SizingInputs {
  capital: number;
  risk_pct: number;
  stop_pct: number;
  max_loss_pct: number;
  guard_pct: number;
  adv_inr: number;
  participation_pct: number;
  win_prob: number;
  payoff_ratio: number;
  kelly_fraction: number;
}

export interface SizingConstraint {
  name: string;
  notional: number;
  note: string;
}

export interface SizingResult {
  constraints: SizingConstraint[];
  binding: string;
  recommended_notional: number;
  recommended_pct: number;
  notes: string[];
}

/** Mandate-aligned defaults (drawdown soft −12 / hard −20); the human sets capital + ADV. */
export const SIZING_DEFAULTS: SizingInputs = {
  capital: 1_000_000,
  risk_pct: 1,
  stop_pct: 8,
  max_loss_pct: 12,
  guard_pct: 20,
  adv_inr: 0,
  participation_pct: 10,
  win_prob: 0.5,
  payoff_ratio: 1.5,
  kelly_fraction: 0.25,
};
