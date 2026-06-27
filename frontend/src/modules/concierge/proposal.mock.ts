// Track-U mock for the inline Orff conversation demo (cone + downside-first
// proposal + feed state). Triggered client-side by the `/proposal` command — no
// API, no storage. The proposal is the Phase-0 `ApprovalProposal` contract; the
// execution orders + sources are demo-only (they have no Phase-0 shape yet).
import type { ApprovalProposal } from "@/modules/contracts";

export const PROPOSAL_DEMO: ApprovalProposal = {
  thesis: "Bank Nifty mean-reversion",
  notional: 320000,
  expected_shortfall: -142000,
  median: 38000,
  stress: -210000,
  red_team: [
    "Crowded trade — the same mean-reversion signal is live across 3 of your books; a correlated unwind hits all at once.",
    "Backtest spans only 14 months. No 2020-style gap-down is in the sample, so the stress loss is an estimate, not a measurement.",
    "Liquidity thins after 14:30 IST; the modelled slippage understates a fast exit.",
  ],
  tenth_man:
    "If the RBI surprises on rates Thursday, the underlying gaps through the hedge leg and the floor breaks before stops fill.",
  runner_ups: [
    "Long straddle · buy vol — richer θ-bleed; −EV while IV stays bid",
    "Sit the event out — safe, but forgoes the 78th-pct IV richness",
  ],
  tripwires: [
    "IV crush > 8 vol points intraday",
    "Underlying breaks 47,200 on close",
    "2-day RSI > 70 — mean-reversion thesis void",
  ],
  calibration: { cleared: 13, hit_stop: 4, open: 3 },
  cooldown_s: 12,
};

export const EXEC_ORDERS: Array<{ ord: string; side: "sell" | "buy" | "guard" }> = [
  { ord: "SELL 2 × BANKNIFTY 47000 PE @ 184", side: "sell" },
  { ord: "BUY  2 × BANKNIFTY 46500 PE @ 121", side: "buy" },
  { ord: "SET stop · underlying close > 47,200", side: "guard" },
];

export const SOURCES = [
  { n: "1", ttl: "NSE option-chain — BANKNIFTY IV percentile", meta: "live · 14:02", fresh: true },
  { n: "2", ttl: "RBI decision study — gap stats 2023–26", meta: "web · 2d", fresh: false },
  { n: "3", ttl: "Your trade log — 11 prior BNF reversions", meta: "live", fresh: true },
];
