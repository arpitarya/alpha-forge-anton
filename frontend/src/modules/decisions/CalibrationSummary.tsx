import type { Calibration } from "@/modules/contracts/approval.types";

/** The calibration scoreboard — "13 cleared · 4 stop · 3 open". This is the same
 * record the inline ApprovalCard's calibration chip references, so a proposal's
 * track record is read against the journal, not asserted in isolation. */
export function CalibrationSummary({ calib }: { calib: Calibration }) {
  const total = calib.cleared + calib.hit_stop + calib.open;
  return (
    <div>
      <div className="of-sub" style={{ marginTop: 0 }}>
        Calibration · {total} decisions resolved
      </div>
      <div className="of-calib">
        <div className="cell cleared">
          <div className="n of-num">{calib.cleared}</div>
          <div className="k">cleared cone</div>
        </div>
        <div className="cell stop">
          <div className="n of-num">{calib.hit_stop}</div>
          <div className="k">hit stop</div>
        </div>
        <div className="cell">
          <div className="n of-num">{calib.open}</div>
          <div className="k">open</div>
        </div>
      </div>
    </div>
  );
}
