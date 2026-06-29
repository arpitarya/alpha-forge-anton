"use client";

import { useEffect, useState } from "react";
import { EdgeAuthor } from "./EdgeAuthor";
import { fetchTemplates } from "./flow.api";
import type { AuthorEdgeRequest, EdgeTemplate, FlowState } from "./flow.types";
import { IdeaTemplates } from "./IdeaTemplates";

const BLANK: AuthorEdgeRequest = {
  hypothesis: "",
  universe: [],
  signal: "momentum",
  holding_period_days: 5,
  expected_edge_pct: 0,
  factor: null,
};

/** The Idea → Rule authoring flow: browse templates (Idea), seed + edit the form (Rule),
 *  pre-register to elgar. Mounted when the cockpit is in "author a new edge" mode. */
export function FlowAuthorPanel({ onAuthored }: { onAuthored: (flow: FlowState) => void }) {
  const [templates, setTemplates] = useState<EdgeTemplate[]>([]);
  const [pickedId, setPickedId] = useState<string | null>(null);
  const [seed, setSeed] = useState<AuthorEdgeRequest>(BLANK);

  useEffect(() => {
    let alive = true;
    fetchTemplates()
      .then((t) => alive && setTemplates(t))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  function pick(t: EdgeTemplate) {
    setPickedId(t.id);
    setSeed({ ...t.prefill });
  }

  return (
    <div className="of-author-panel" data-author-panel>
      <div className="of-stage-head">
        <span className="of-lbl acc">Idea</span>
        <h3>Pick a candidate family</h3>
      </div>
      <IdeaTemplates templates={templates} selectedId={pickedId} onPick={pick} />
      <div className="of-stage-head" style={{ marginTop: 18 }}>
        <span className="of-lbl acc">Rule</span>
        <h3>Author + pre-register the rule</h3>
      </div>
      <EdgeAuthor key={pickedId ?? "blank"} seed={seed} onAuthored={onAuthored} />
    </div>
  );
}
