import type { Objective } from "@/modules/contracts";
import type { GoalsLive } from "./goals.mock";

/** Tier 1 (aim banner) + Tier 2 (Calmar hero + drawdown-guard meter). The meter
 * track runs 0 → 1.25× the hard floor so the −12 soft and −20 hard marks sit at
 * fixed positions; the fill is the live trailing drawdown. */
export function GoalsScore({ obj, live }: { obj: Objective; live: GoalsLive }) {
  const pendingC = live.calmar == null;
  const pendingD = live.current_dd == null;
  const track = Math.abs(obj.drawdown_guard.hard) * 1.25; // -25 when hard = -20
  const pct = (v: number) => `${(Math.min(Math.abs(v), track) / track) * 100}%`;
  return (
    <>
      <div className="of-aim">
        <h4>{obj.aim}</h4>
        <div className="sub">
          {pendingC ? (
            <span>not yet measurable</span>
          ) : (
            <>
              <span>Calmar {obj.calmar_target}</span>
              <span className="dotsep">·</span>
              <span>pays its own way</span>
              <span className="dotsep">·</span>
              <span>every result proven</span>
            </>
          )}
        </div>
      </div>

      <div className="of-score">
        <div className="of-calmar">
          <div className="k">Calmar</div>
          <div className="big of-num" style={pendingC ? { color: "var(--fg-4)" } : undefined}>
            {pendingC ? (
              "—"
            ) : (
              <>
                {live.calmar}
                <span className="unit">×</span>
              </>
            )}
          </div>
          <div className="band">
            <span>
              target&nbsp;<b>{obj.calmar_target.toFixed(1)}</b>
            </span>
            <span>
              floor&nbsp;<b>{obj.calmar_floor.toFixed(1)}</b>
            </span>
          </div>
          <div className="cap" style={pendingC ? { color: "var(--fg-4)" } : undefined}>
            {pendingC ? "needs ≥ 90 trading days" : "~60% CAGR within −20%"}
          </div>
        </div>

        <div className="of-ddg">
          <div className="top">
            <span className="of-lbl">Drawdown guard</span>
            <span className="now of-num" style={pendingD ? { color: "var(--fg-4)" } : undefined}>
              {pendingD ? "pending" : `${live.current_dd}%`}
            </span>
          </div>
          <div
            className={`of-meter${pendingD ? " of-pending" : ""}`}
            style={pendingD ? { background: "transparent" } : undefined}
          >
            {!pendingD && live.current_dd != null && (
              <div className="fill" style={{ width: pct(live.current_dd) }} />
            )}
            <div className="mk soft" style={{ left: pct(obj.drawdown_guard.soft) }}>
              <span className="tag">{obj.drawdown_guard.soft}% soft</span>
            </div>
            <div className="mk hard" style={{ left: pct(obj.drawdown_guard.hard) }}>
              <span className="tag" style={{ left: "auto", right: 4 }}>
                {obj.drawdown_guard.hard}% hard
              </span>
            </div>
          </div>
          <div className="scale">
            <span>0%</span>
            <span>{obj.drawdown_guard.soft}%</span>
            <span>{obj.drawdown_guard.hard}%</span>
            <span>−{track}%</span>
          </div>
        </div>
      </div>
    </>
  );
}
