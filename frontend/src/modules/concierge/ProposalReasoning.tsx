"use client";

import { useState } from "react";
import type { ApprovalProposal } from "@/modules/contracts";

const SEV = ["high", "med", "low"] as const;

/**
 * Balanced reasoning: the top 1–2 red-team objections are always shown; the full
 * red-team, the mandatory 10th-Man dissent, runner-ups and tripwires sit behind
 * one "show the full case" control so the card stays scannable without hiding the
 * work.
 */
export function ProposalReasoning({ p }: { p: ApprovalProposal }) {
  const [open, setOpen] = useState(false);
  const top = p.red_team.slice(0, 2);
  const rest = p.red_team.slice(2);
  return (
    <>
      <div className="of-sub">Red-team · top objections</div>
      <div className="of-obj">
        {top.map((txt, i) => (
          <div className="row" key={txt}>
            <span className={`of-sev ${SEV[i] ?? "low"}`}>{SEV[i] ?? "low"}</span>
            <p>{txt}</p>
          </div>
        ))}
      </div>

      <button
        type="button"
        className="of-why"
        style={{ marginTop: 12 }}
        onClick={() => setOpen((o) => !o)}
      >
        {open ? "Hide full case ▴" : "Show 10th-Man, runner-ups & tripwires ▾"}
      </button>

      {open && (
        <div data-reasoning-expanded>
          {rest.map((txt, i) => (
            <div className="of-obj" key={txt} style={{ marginTop: 8 }}>
              <div className="row">
                <span className={`of-sev ${SEV[i + 2] ?? "low"}`}>{SEV[i + 2] ?? "low"}</span>
                <p>{txt}</p>
              </div>
            </div>
          ))}

          <div className="of-tenth">
            <div className="k">◎ 10th-Man · here's how this could still kill us</div>
            <p>{p.tenth_man}</p>
          </div>

          <div className="of-sub">Why this — not those</div>
          <div className="of-runners">
            {p.runner_ups.map((r) => {
              const [name, note] = r.split(" — ");
              return (
                <div className="of-runner" key={r}>
                  <span className="l">
                    <b>{name}</b>
                  </span>
                  {note && <span className="x note">{note}</span>}
                </div>
              );
            })}
          </div>

          <div className="of-sub">Plan tripwires · thesis-breakers</div>
          <div className="of-trip">
            {p.tripwires.map((t) => (
              <div className="t" key={t}>
                <span className="wire" />
                {t}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
