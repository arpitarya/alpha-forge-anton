import type { ApprovalProposal } from "@/modules/contracts";
import { Num } from "@/modules/forge";

const inr = (n: number) => `${n < 0 ? "−" : "+"}₹${Math.abs(n).toLocaleString("en-IN")}`;

/** The downside-first Expected-Shortfall hero — the largest figure on the card.
 * Tapping it is the explicit acknowledgement that gates Approve. Median + stress
 * are secondary. */
export function ProposalHero({
  p,
  acked,
  onAck,
}: {
  p: ApprovalProposal;
  acked: boolean;
  onAck: () => void;
}) {
  return (
    <div className={`of-loss${acked ? " acked" : ""}`}>
      <div className="k">Expected shortfall · worst 1-in-20</div>
      <button type="button" className="ack" onClick={() => !acked && onAck()}>
        <Num v={inr(p.expected_shortfall)} kind={acked ? "gain" : "loss"} big={42} glow />
      </button>
      <span className="hint">
        {acked ? "✓ loss acknowledged" : "tap the loss to acknowledge ↑"}
      </span>
      <div className="secondary">
        <div className="it">
          <div className="kk">Median outcome</div>
          <div className="vv up of-num">{inr(p.median)}</div>
        </div>
        <div className="it">
          <div className="kk">Stress (RBI gap)</div>
          <div className="vv of-num">{inr(p.stress)}</div>
        </div>
      </div>
    </div>
  );
}
