import type { DecisionRow } from "@/modules/contracts";
import type { Calibration } from "@/modules/contracts/approval.types";
import { CalibrationSummary } from "./CalibrationSummary";
import { DecisionRowCard } from "./DecisionRowCard";

/** The replayable prove-it ledger: a calibration scoreboard over the journal of
 * every decision (proposal → downside-shown → decision → outcome → replay). */
export function DecisionsLedger({ rows, calib }: { rows: DecisionRow[]; calib: Calibration }) {
  return (
    <div>
      <CalibrationSummary calib={calib} />
      <div className="of-sub">Decision journal · {rows.length} recent</div>
      <div className="of-ledger" style={{ marginTop: 0 }}>
        {rows.map((row) => (
          <DecisionRowCard key={`${row.date}-${row.proposal.thesis}`} row={row} />
        ))}
      </div>
    </div>
  );
}
