import type { Objective } from "@/modules/contracts";
import type { GoalsLive } from "./goals.mock";

const lakh = (n: number) => `₹${(n / 100000).toFixed(1)}L`;
const inr = (n: number) => `₹${Math.round(n).toLocaleString("en-IN")}`;

/** Tier 3 (edge library — honest-pending, never a faked 0%) + the self-funding
 * strip + the capital-structure bar (Groww + Zerodha at-risk, Reserve LOCKED). */
export function GoalsStructure({
  obj,
  live,
  pending,
}: {
  obj: Objective;
  live: GoalsLive;
  pending: boolean;
}) {
  const cs = obj.capital_structure;
  const total = cs.groww + cs.zerodha + cs.reserve || 1;
  const w = (n: number) => `${(n / total) * 100}%`;
  return (
    <>
      <div className="of-edges">
        <div className="hero">
          <span className="n of-num" style={pending ? { color: "var(--fg-4)" } : undefined}>
            {live.edges}
          </span>
          <div className="of-lbl">/ {live.edges_target} live edges</div>
        </div>
        <div className="of-edgetrack of-pending">
          <span className="of-pending-lbl">
            {pending
              ? "no validated edges yet — pending"
              : "awaiting first validated edge — pending"}
          </span>
        </div>
        <div className="caps">
          <span className="of-chip">kill-rate ≥ 80%</span>
          <span className="of-chip">this quarter</span>
        </div>
      </div>

      {/* Self-funding strip — covered:false → "not yet covered" */}
      <div className="of-fund" style={pending ? { borderStyle: "dashed" } : undefined}>
        <span
          className="pin"
          style={pending ? { background: "var(--fg-4)", boxShadow: "none" } : undefined}
        />
        <span>
          opex&nbsp;<b style={{ color: "var(--fg)" }}>{inr(obj.self_funding.opex_per_month)}</b>/mo
        </span>
        <span className="dotsep">·</span>
        <span>reserve pending</span>
        <span className="dotsep">·</span>
        <span className="neg">{obj.self_funding.covered ? "covered" : "not yet covered"}</span>
      </div>

      {/* Capital structure — collapsed details row; Groww + Zerodha at-risk, Reserve a LOCKED stripe */}
      <details className="of-struct">
        <summary className="of-lbl" style={{ cursor: "pointer", listStyle: "none" }}>
          Capital structure ▸
        </summary>
        {pending ? (
          <div className="of-edgetrack of-pending" style={{ marginTop: 10, height: 16 }}>
            <span className="of-pending-lbl">connect brokers to fund — pending</span>
          </div>
        ) : (
          <>
            <div className="of-structbar">
              <span className="s-groww" style={{ width: w(cs.groww) }} />
              <span className="s-zer" style={{ width: w(cs.zerodha) }} />
              <span className="s-res" style={{ width: w(cs.reserve) }} />
            </div>
            <div className="of-leg">
              <div className="it">
                <span className="sw g" />
                Groww <span className="amt">{lakh(cs.groww)}</span>
              </div>
              <div className="it">
                <span className="sw z" />
                Zerodha <span className="amt">{lakh(cs.zerodha)}</span>
              </div>
              <div className="it">
                <span className="sw r" />
                Reserve <span className="amt">{lakh(cs.reserve)}</span>{" "}
                <span className="lock">🔒 not at-risk</span>
              </div>
            </div>
          </>
        )}
      </details>
    </>
  );
}
