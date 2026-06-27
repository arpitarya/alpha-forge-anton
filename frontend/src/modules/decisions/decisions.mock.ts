// Track-U mock for the Decisions surface — the replayable prove-it ledger.
// Shapes are the Phase-0 `DecisionRow` / `ApprovalProposal` / `Calibration`
// contracts (imported, never re-declared). The CALIBRATION scoreboard the
// approval chip references is 13 cleared · 4 stop · 3 open. ₹ are worked-example
// figures, not real positions. React state only; real data lands in Phase 3.
import type { ApprovalProposal, DecisionRow } from "@/modules/contracts";
import type { Calibration } from "@/modules/contracts/approval.types";

export const CALIBRATION_MOCK: Calibration = { cleared: 13, hit_stop: 4, open: 3 };

function proposal(thesis: string, over: Partial<ApprovalProposal> = {}): ApprovalProposal {
  return {
    thesis,
    notional: 320000,
    expected_shortfall: -142000,
    median: 38000,
    stress: -210000,
    red_team: [
      "Crowded trade — the same signal is live across 3 books; a correlated unwind hits all at once.",
      "Backtest spans only 14 months — no 2020-style gap-down is in the sample.",
    ],
    tenth_man:
      "If the RBI surprises on rates, the underlying gaps through the hedge before stops fill.",
    runner_ups: ["Long straddle · richer θ-bleed", "Sit the event out · forgoes the IV richness"],
    tripwires: ["IV crush > 8 vol points intraday", "Underlying breaks 47,200 on close"],
    calibration: CALIBRATION_MOCK,
    cooldown_s: 12,
    ...over,
  };
}

export const DECISIONS_MOCK: DecisionRow[] = [
  {
    date: "Jun 27",
    proposal: proposal("Bank Nifty mean-reversion into RBI"),
    downside_shown: -142000,
    decision: "approved",
    outcome: "open",
    replayable: true,
  },
  {
    date: "Jun 18",
    proposal: proposal("IT momentum basket", { notional: 250000, expected_shortfall: -98000 }),
    downside_shown: -98000,
    decision: "vetoed",
    outcome: "open",
    replayable: true,
  },
  {
    date: "Jun 11",
    proposal: proposal("Gold hedge sleeve +4%", { notional: 180000, expected_shortfall: -54000 }),
    downside_shown: -54000,
    decision: "approved",
    outcome: "cleared_cone",
    replayable: true,
  },
  {
    date: "Jun 04",
    proposal: proposal("Reliance covered call", { notional: 210000, expected_shortfall: -61000 }),
    downside_shown: -61000,
    decision: "approved",
    outcome: "hit_stop",
    replayable: false,
  },
];
