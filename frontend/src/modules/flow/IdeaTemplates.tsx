"use client";

import { clsx } from "clsx";
import type { EdgeTemplate } from "./flow.types";

/** Idea-stage browser — pick a candidate family to seed the Rule-stage form.
 *  Family A/B are real (engine runs them); Family C is scaffolded (`available=false`) and
 *  cannot be authored yet — shown, not hidden, with an honest "engine deferred" tag. */
export function IdeaTemplates({
  templates,
  selectedId,
  onPick,
}: {
  templates: EdgeTemplate[];
  selectedId: string | null;
  onPick: (t: EdgeTemplate) => void;
}) {
  return (
    <div className="of-ideas" data-idea-templates>
      {templates.map((t) => (
        <button
          key={t.id}
          type="button"
          data-template={t.id}
          disabled={!t.available}
          className={clsx("of-idea", selectedId === t.id && "sel", !t.available && "of-pending")}
          onClick={() => onPick(t)}
        >
          <div className="of-idea-head">
            <span className="of-chip acc">Family {t.family}</span>
            {!t.available && <span className="of-pending-lbl">engine deferred</span>}
          </div>
          <div className="of-idea-name">{t.name}</div>
          <p className="of-idea-desc">{t.description}</p>
        </button>
      ))}
    </div>
  );
}
