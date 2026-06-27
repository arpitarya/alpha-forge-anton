"use client";

import { useState } from "react";
import type { DecisionRow } from "@/modules/contracts";
import { Num } from "@/modules/forge";

const inr = (n: number) => `${n < 0 ? "−" : ""}₹${Math.abs(n).toLocaleString("en-IN")}`;
const OUTCOME: Record<DecisionRow["outcome"], string> = {
  cleared_cone: "cleared cone",
  hit_stop: "hit stop",
  open: "open",
};
const OC_CLASS: Record<DecisionRow["outcome"], string> = {
  cleared_cone: "cleared",
  hit_stop: "stop",
  open: "open",
};

/** One journal row: the proposal seen → the downside that was SHOWN → the
 * decision → the outcome, plus REPLAY (enabled only when the inputs were captured
 * well enough to re-run the call). Replay is read-only and deterministic (mock). */
export function DecisionRowCard({ row }: { row: DecisionRow }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <div className="of-drow">
        <span className="dt">{row.date}</span>
        <div>
          <div className="nm">{row.proposal.thesis}</div>
          <div className="shown">
            <span>{inr(row.proposal.notional)} notional · downside shown</span>
            <span className="ds">{inr(row.downside_shown)}</span>
          </div>
        </div>
        <div className="right">
          <span className={`of-oc ${row.decision === "vetoed" ? "veto" : OC_CLASS[row.outcome]}`}>
            {row.decision === "vetoed" ? "vetoed" : OUTCOME[row.outcome]}
          </span>
          <button
            type="button"
            className="of-replay"
            disabled={!row.replayable}
            title={row.replayable ? "Re-run this decision" : "Inputs not captured — cannot replay"}
            onClick={() => setOpen((o) => !o)}
          >
            ⟲ Replay
          </button>
        </div>
      </div>
      {open && row.replayable && (
        <div className="of-replay-out">
          Re-ran on captured inputs · ES then{" "}
          <Num v={inr(row.proposal.expected_shortfall)} kind="loss" /> · median{" "}
          <Num v={inr(row.proposal.median)} kind="gain" /> · decision {row.decision} —
          byte-identical.
        </div>
      )}
    </div>
  );
}
