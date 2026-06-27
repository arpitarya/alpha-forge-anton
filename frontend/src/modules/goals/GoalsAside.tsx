import Link from "next/link";
import { OBJECTIVE_MOCK } from "./goals.mock";

const lakh = (n: number) => `₹${(n / 100000).toFixed(1)}L`;

const RECENT = [
  { dt: "Jun 18", nm: "IT momentum basket", st: "vetoed · too crowded", cls: "veto" },
  { dt: "Jun 11", nm: "Gold hedge sleeve +4%", st: "approved · live", cls: "app" },
  { dt: "Jun 04", nm: "Reliance covered call", st: "approved · closed +₹22k", cls: "app" },
];

/** Right rail beside the editable panel: capital at-risk vs reserved, plus a
 * compact proposal-log preview that links to the full replayable Decisions ledger. */
export function GoalsAside() {
  const cs = OBJECTIVE_MOCK.capital_structure;
  const atRisk = cs.groww + cs.zerodha;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="of-calib">
        <div className="cell">
          <div className="n of-num">{lakh(atRisk)}</div>
          <div className="k">At-risk · Groww + Zerodha</div>
        </div>
        <div className="cell">
          <div className="n of-num">{lakh(cs.reserve)}</div>
          <div className="k">🔒 Reserve · not at-risk</div>
        </div>
      </div>

      <div>
        <div className="of-sub" style={{ marginTop: 4 }}>
          Proposal log · approver: you
        </div>
        <div className="of-ledger" style={{ marginTop: 0 }}>
          {RECENT.map((r) => (
            <div className="of-drow" key={r.nm} style={{ gridTemplateColumns: "64px 1fr auto" }}>
              <span className="dt">{r.dt}</span>
              <span className="nm">{r.nm}</span>
              <span className={`of-oc ${r.cls}`}>{r.st}</span>
            </div>
          ))}
        </div>
        <Link
          href="/decisions"
          className="of-why"
          style={{ display: "inline-block", marginTop: 12, textDecoration: "none" }}
        >
          View the replayable ledger →
        </Link>
      </div>
    </div>
  );
}
