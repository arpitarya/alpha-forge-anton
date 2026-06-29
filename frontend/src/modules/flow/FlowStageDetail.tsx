"use client";

import { ApprovePanel } from "./ApprovePanel";
import type { StageStatus } from "./flow.types";
import { LivePanel } from "./LivePanel";
import { PlanSizingPanel } from "./PlanSizingPanel";
import { RangeConePanel } from "./RangeConePanel";
import { RedteamPanel } from "./RedteamPanel";
import { TestRunPanel } from "./TestRunPanel";
import { WatchPanel } from "./WatchPanel";

/** The selected stage's detail card — its label, state, and one-line summary, plus the
 *  stage's working surface: Test = the funnel run (gates), Range = the outcome cone.
 *  `na`/`blocked` stages carry an explicit honest-pending note (never a faked artifact). */
export function FlowStageDetail({
  detail,
  edgeId,
  onRunComplete,
}: {
  detail: StageStatus;
  edgeId: string;
  onRunComplete: () => void;
}) {
  return (
    <div className="of-stage-detail" data-stage-detail data-state={detail.state}>
      <div className="of-stage-head">
        <span className="of-lbl acc">{detail.label}</span>
        <span className={`of-chip ${detail.state === "blocked" ? "bad" : ""}`}>{detail.state}</span>
      </div>
      <p>{detail.summary || "—"}</p>
      {detail.id === "test" && <TestRunPanel edgeId={edgeId} onComplete={onRunComplete} />}
      {detail.id === "range" && <RangeConePanel edgeId={edgeId} />}
      {detail.id === "plan" && detail.state === "active" && <PlanSizingPanel />}
      {detail.id === "redteam" && detail.state === "active" && <RedteamPanel edgeId={edgeId} />}
      {detail.id === "approve" && detail.state === "active" && <ApprovePanel edgeId={edgeId} />}
      {detail.id === "live" && detail.state === "active" && <LivePanel edgeId={edgeId} />}
      {detail.id === "watch" && detail.state === "active" && <WatchPanel edgeId={edgeId} />}
    </div>
  );
}
