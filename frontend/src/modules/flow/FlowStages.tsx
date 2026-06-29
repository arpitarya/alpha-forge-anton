"use client";

import { clsx } from "clsx";
import type { StageId, StageStatus } from "./flow.types";

/** The locked process-flow rail — every stage rendered with its real state. `na`/`blocked`
 *  stages show honest-pending styling (never a faked "done"); the selected stage highlights. */
export function FlowStages({
  stages,
  selected,
  onSelect,
}: {
  stages: StageStatus[];
  selected: StageId | null;
  onSelect: (id: StageId) => void;
}) {
  return (
    <div className="of-flow-rail" data-flow-rail>
      {stages.map((s, i) => (
        <div key={s.id} className="of-flow-node">
          {i > 0 && <span className="of-flow-conn" aria-hidden />}
          <button
            type="button"
            data-stage={s.id}
            data-state={s.state}
            className={clsx("of-flow-stage", `st-${s.state}`, selected === s.id && "sel")}
            onClick={() => onSelect(s.id)}
            title={s.summary}
          >
            <span className="of-flow-dot" aria-hidden />
            <span className="of-flow-label">{s.label}</span>
            <span className="of-flow-sub">{s.summary || STATE_WORD[s.state]}</span>
          </button>
        </div>
      ))}
    </div>
  );
}

const STATE_WORD: Record<StageStatus["state"], string> = {
  done: "done",
  active: "in progress",
  pending: "pending",
  na: "not yet built",
  blocked: "gated",
};
