"use client";

import { type ReactNode, useState } from "react";

export interface WwwRow {
  tag: string;
  sm: ReactNode;
  body: ReactNode;
  err?: boolean;
}

/** What / why / how — every grounded recommendation carries this. The first row
 * is open by default; the rest expand on tap. Orff shows its work rather than
 * asking to be believed. */
export function Www({ rows, defaultOpen = 0 }: { rows: WwwRow[]; defaultOpen?: number }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="of-www">
      {rows.map((r, i) => (
        <div className={`row${open === i ? " open" : ""}`} key={r.tag}>
          <button type="button" className="head" onClick={() => setOpen(open === i ? -1 : i)}>
            <span className={`tg${r.err ? " err" : ""}`}>{r.tag}</span>
            <span className="sm">{r.sm}</span>
            <span className="car">›</span>
          </button>
          <div className="body">{r.body}</div>
        </div>
      ))}
    </div>
  );
}
