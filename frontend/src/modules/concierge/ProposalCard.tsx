"use client";

import { useState } from "react";
import type { ApprovalProposal } from "@/modules/contracts";
import { Num, UChip } from "@/modules/forge";
import { ExecChecklist } from "./ExecChecklist";
import { ProposalFoot } from "./ProposalFoot";
import { ProposalHero } from "./ProposalHero";
import { ProposalReasoning } from "./ProposalReasoning";
import { VetoPicker } from "./VetoPicker";

const inr = (n: number) => `${n < 0 ? "−" : "+"}₹${Math.abs(n).toLocaleString("en-IN")}`;
type Phase = "await" | "acked" | "approved" | "vetoing" | "vetoed";

/**
 * Downside-first trade proposal (Phase-0 ApprovalProposal). The Expected-Shortfall
 * is the largest figure and Approve is GATED behind an explicit tap on that loss
 * (a deliberate acceptance of the worst case, not a reflex click). Binary only —
 * Approve-as-proposed or Veto-with-reason; no inline size/price edits. A STALE
 * feed blocks Approve. Never auto-executes.
 */
export function ProposalCard({ p, feedStale }: { p: ApprovalProposal; feedStale: boolean }) {
  const [phase, setPhase] = useState<Phase>("await");
  const [reason, setReason] = useState("");
  const acked = phase === "acked";
  const canApprove = acked && !feedStale;

  const Head = (
    <div className="of-ap-head">
      <div>
        <div className="name">{p.thesis}</div>
        <div className="meta">
          ₹{(p.notional / 100000).toFixed(1)}L notional · 2-day hold · red-teamed
        </div>
      </div>
      <UChip tone="acc">{p.calibration.cleared} cleared</UChip>
    </div>
  );

  if (phase === "vetoed")
    return (
      <div>
        {Head}
        <div className="of-cooldown" style={{ marginTop: 14, justifyContent: "flex-start" }}>
          ✕ vetoed &amp; logged — "{reason}". Plan stays vetted; nothing entered the book.
        </div>
      </div>
    );
  if (phase === "vetoing")
    return (
      <div>
        {Head}
        <VetoPicker
          onLog={(r) => {
            setReason(r);
            setPhase("vetoed");
          }}
          onBack={() => setPhase("await")}
        />
      </div>
    );
  if (phase === "approved")
    return (
      <div>
        {Head}
        <div className="of-loss acked" style={{ marginTop: 14 }}>
          <div className="k">Downside acknowledged</div>
          <div className="ack">
            <Num v={inr(p.expected_shortfall)} kind="gain" big={38} glow />
          </div>
          <span className="hint">✓ tapped &amp; logged</span>
        </div>
        <ExecChecklist />
      </div>
    );

  return (
    <div>
      {Head}
      <ProposalHero p={p} acked={acked} onAck={() => setPhase("acked")} />
      <ProposalReasoning p={p} />
      <ProposalFoot
        canApprove={canApprove}
        feedStale={feedStale}
        acked={acked}
        cooldownS={p.cooldown_s}
        onApprove={() => setPhase("approved")}
        onVeto={() => setPhase("vetoing")}
      />
    </div>
  );
}
