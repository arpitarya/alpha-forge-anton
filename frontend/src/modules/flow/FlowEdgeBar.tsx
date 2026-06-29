"use client";

import type { EdgeListItem } from "./flow.types";

/** The cockpit's top bar — the edge picker plus "New edge" (enters authoring mode). */
export function FlowEdgeBar({
  edges,
  activeId,
  authoring,
  onOpen,
  onNew,
}: {
  edges: EdgeListItem[];
  activeId: string | null;
  authoring: boolean;
  onOpen: (edgeId: string) => void;
  onNew: () => void;
}) {
  return (
    <div className="of-cockpit-bar">
      <div className="of-edge-picker">
        {edges.map((e) => (
          <button
            key={e.edge_id}
            type="button"
            data-edge={e.edge_id}
            className={`of-edge ${!authoring && activeId === e.edge_id ? "sel" : ""}`}
            onClick={() => onOpen(e.edge_id)}
          >
            <span className="nm">{e.edge_id}</span>
            {e.frozen && <span className="of-chip">frozen</span>}
          </button>
        ))}
      </div>
      <button
        type="button"
        className={`of-btn ${authoring ? "primary" : ""}`}
        data-new-edge
        onClick={onNew}
      >
        ＋ New edge
      </button>
    </div>
  );
}
