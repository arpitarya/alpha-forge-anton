import type { Objective } from "@/modules/contracts";
import type { GoalsLive } from "./goals.mock";

const lakh = (n: number) => `₹${(n / 100000).toFixed(1)}L`;
const inr = (n: number) => `₹${Math.round(n).toLocaleString("en-IN")}`;
const fg = { color: "var(--fg)", fontWeight: 600 } as const;
const sep = { opacity: 0.4, fontStyle: "normal" } as const;

/** Tier 3 (edge library — the discovery-journal funnel, honest-empty when nothing
 * is live yet, never a faked 0% bar) + the self-funding strip + the capital-structure
 * bar (Groww + Zerodha at-risk, Reserve LOCKED). All values are the real mandate. */
export function GoalsStructure({ obj, live }: { obj: Objective; live: GoalsLive }) {
  const cs = obj.capital_structure;
  const total = cs.groww + cs.zerodha + cs.reserve || 1;
  const w = (n: number) => `${(n / total) * 100}%`;
  const noEdges = live.tested === 0;
  return (
    <>
      <div className="of-edges">
        <div className="hero">
          <span className="n of-num">{live.edges}</span>
          <div className="of-lbl">/ {live.edges_target} live edges</div>
        </div>
        {noEdges ? (
          <div className="of-edgetrack of-pending">
            <span className="of-pending-lbl">no validated edges yet — pending</span>
          </div>
        ) : (
          <div className="of-edgestat" data-edge-stat>
            <b style={fg}>{live.tested}</b> tested<i style={sep}>·</i>
            <b style={fg}>{live.killed}</b> killed<i style={sep}>·</i>
            <b style={fg}>{live.edges}</b> live<i style={sep}>·</i>
            <b style={fg}>{Math.round(live.kill_rate * 100)}%</b> kill-rate
          </div>
        )}
        <div className="caps">
          <span className="of-chip">kill-rate ≥ 80%</span>
          <span className="of-chip">this quarter</span>
        </div>
      </div>

      {/* Self-funding strip — covered:null → "not yet covered" (honest-pending) */}
      <div className="of-fund">
        <span className="pin" />
        <span>
          opex&nbsp;<b style={{ color: "var(--fg)" }}>{inr(obj.self_funding.opex_per_month)}</b>/mo
        </span>
        <span className="dotsep">·</span>
        <span>reserve {lakh(obj.self_funding.reserve)}</span>
        <span className="dotsep">·</span>
        <span className="neg">{obj.self_funding.covered ? "covered" : "not yet covered"}</span>
      </div>

      {/* Capital structure — Groww + Zerodha at-risk, Reserve a LOCKED stripe */}
      <details className="of-struct">
        <summary className="of-lbl" style={{ cursor: "pointer", listStyle: "none" }}>
          Capital structure ▸
        </summary>
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
      </details>
    </>
  );
}
