"use client";

import { useCallback, useEffect, useState } from "react";
import { FlowAuthorPanel } from "./FlowAuthorPanel";
import { FlowEdgeBar } from "./FlowEdgeBar";
import { FlowStageDetail } from "./FlowStageDetail";
import { FlowStages } from "./FlowStages";
import { fetchEdges, fetchFlowState } from "./flow.api";
import type { EdgeListItem, FlowState, StageId } from "./flow.types";

const activeOr = (f: FlowState, fallback: StageId): StageId =>
  f.stages.find((s) => s.state === "active")?.id ?? f.stages[0]?.id ?? fallback;

/** The cockpit spine — pick an edge (or author a new one), see all 9 stages with real
 *  per-stage status, and inspect the selected stage. A view over edge state, not a new
 *  engine; downstream stages render honest-pending until their slices land. */
export function FlowCockpit() {
  const [edges, setEdges] = useState<EdgeListItem[]>([]);
  const [flow, setFlow] = useState<FlowState | null>(null);
  const [authoring, setAuthoring] = useState(false);
  const [sel, setSel] = useState<StageId | null>(null);

  const refresh = useCallback(
    () =>
      fetchEdges()
        .then(setEdges)
        .catch(() => {}),
    [],
  );

  const open = useCallback(async (edgeId: string) => {
    setAuthoring(false);
    const f = await fetchFlowState(edgeId).catch(() => null);
    setFlow(f);
    setSel(f ? activeOr(f, "idea") : null);
  }, []);

  useEffect(() => {
    fetchEdges()
      .then((list) => {
        setEdges(list);
        if (list[0]) void open(list[0].edge_id);
      })
      .catch(() => {});
  }, [open]);

  function onAuthored(f: FlowState) {
    setFlow(f);
    setAuthoring(false);
    setSel(activeOr(f, "rule"));
    void refresh();
  }

  // After a run completes: refresh the Test verdict + edge list WITHOUT changing the selected stage.
  const reloadFlow = useCallback(async () => {
    if (!flow) return;
    const f = await fetchFlowState(flow.edge_id).catch(() => null);
    if (f) setFlow(f);
    void refresh();
  }, [flow, refresh]);

  const detail = flow?.stages.find((s) => s.id === sel) ?? null;

  return (
    <div className="of-cockpit" data-flow-cockpit>
      <FlowEdgeBar
        edges={edges}
        activeId={flow?.edge_id ?? null}
        authoring={authoring}
        onOpen={(id) => void open(id)}
        onNew={() => {
          setAuthoring(true);
          setFlow(null);
        }}
      />

      {authoring ? (
        <FlowAuthorPanel onAuthored={onAuthored} />
      ) : flow ? (
        <>
          <FlowStages stages={flow.stages} selected={sel} onSelect={setSel} />
          {detail && (
            <FlowStageDetail detail={detail} edgeId={flow.edge_id} onRunComplete={reloadFlow} />
          )}
        </>
      ) : (
        <p className="of-pending-lbl" style={{ padding: 20 }}>
          No edges yet — author one to begin.
        </p>
      )}
    </div>
  );
}
