"use client";

import { notify } from "@alphaforge-anton/solar-ui";
import { useSavePlan } from "../plans/plans.query";

interface Props {
  /** The user's question — becomes the plan title (and its slug id). */
  title: string;
  /** The full assistant answer — saved verbatim into the private store. */
  content: string;
}

/**
 * "Save plan" action on an Orff answer → POST /plans → private elgar store.
 * Personal figures are welcome there; they never enter this repo (plan-store).
 */
export function SavePlanButton({ title, content }: Props) {
  const save = useSavePlan();
  return (
    <button
      type="button"
      disabled={save.isPending}
      onClick={() =>
        save.mutate(
          { title, content },
          {
            onSuccess: (r) =>
              notify.ok({ title: "Plan saved to elgar", message: r.ref }),
            onError: (e) =>
              notify.error({ title: "Plan save failed", message: String(e) }),
          },
        )
      }
      style={{
        marginTop: 10,
        padding: "4px 10px",
        borderRadius: 6,
        border: "1px solid var(--line)",
        background: "transparent",
        color: "var(--fg-3)",
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.18em",
        textTransform: "uppercase",
        cursor: save.isPending ? "wait" : "pointer",
      }}
    >
      {save.isPending ? "saving…" : "⬡ save plan → elgar"}
    </button>
  );
}
