/** Binary action footer — Approve-as-proposed (gated on the ack + a live feed) or
 * Veto-with-reason. No inline size/price edits; the vetted plan stays vetted. */
export function ProposalFoot({
  canApprove,
  feedStale,
  acked,
  cooldownS,
  onApprove,
  onVeto,
}: {
  canApprove: boolean;
  feedStale: boolean;
  acked: boolean;
  cooldownS: number;
  onApprove: () => void;
  onVeto: () => void;
}) {
  return (
    <div className="of-ap-foot">
      <div className="btnrow">
        <button
          type="button"
          className={`of-btn ${canApprove ? "primary" : "locked"} full`}
          disabled={!canApprove}
          onClick={() => canApprove && onApprove()}
        >
          {canApprove ? "Approve as proposed →" : "Approve — acknowledge loss first"}
        </button>
        <button type="button" className="of-btn danger full" onClick={onVeto}>
          Veto (with reason)
        </button>
      </div>
      <div className="of-cooldown">
        {feedStale
          ? "⚠ feed stale — approval blocked until it re-grounds"
          : acked
            ? "✓ cooldown elapsed · binary approve-as-proposed or veto"
            : `⏱ large size · ${cooldownS}s logged cooldown — acknowledge the loss to unlock`}
      </div>
    </div>
  );
}
