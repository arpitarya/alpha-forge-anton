/** Live-stage view-models — hand-mirrored from `app/modules/flow/flow_live_schema.py`.
 *  Orff prepares orders + reconciles fills; it NEVER places an order or auto-executes. */

export type OrderSide = "buy" | "sell";
export type OrderKind = "entry" | "guard";
export type GuardState = "ok" | "soft" | "hard";

export interface PreparedOrder {
  side: OrderSide;
  kind: OrderKind;
  label: string;
  notional: number;
  level_pct: number;
}

export interface OrderPlan {
  edge_id: string;
  thesis: string;
  notional: number;
  orders: PreparedOrder[];
  soft_guard_pct: number;
  hard_guard_pct: number;
  checklist: string[];
}

export interface Fill {
  symbol: string;
  qty: number;
  buy_price: number;
  fees: number;
  last_price: number;
}

export interface ReconcileResult {
  invested: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
  slippage: number;
  guard: GuardState;
  notes: string[];
}
