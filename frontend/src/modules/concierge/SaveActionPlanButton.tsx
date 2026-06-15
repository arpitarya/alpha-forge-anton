"use client";

import { notify } from "@alphaforge-anton/solar-ui";
import { useState } from "react";

/**
 * "Save plan → actions" on an Orff /review answer → POST /signals/plan → the private
 * elgar `actions/` ledger. One save = one git commit — the audit trail of the
 * re-runnable plan loop (handoff §7). Personal figures live in elgar, never this repo.
 */
export function SaveActionPlanButton() {
  const [busy, setBusy] = useState(false);
  async function save() {
    setBusy(true);
    try {
      const tok = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
      const res = await fetch("/api/v1/signals/plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(tok ? { Authorization: `Bearer ${tok}` } : {}),
        },
      });
      const r = await res.json().catch(() => ({}));
      if (res.ok) notify.ok({ title: "Plan saved to actions/", message: r.plan_id ?? "" });
      else notify.error({ title: "Save failed", message: `HTTP ${res.status}` });
    } catch (e) {
      notify.error({ title: "Save failed", message: String(e) });
    } finally {
      setBusy(false);
    }
  }
  return (
    <button
      type="button"
      disabled={busy}
      onClick={save}
      style={{
        marginTop: 10,
        marginLeft: 8,
        padding: "4px 10px",
        borderRadius: 6,
        border: "1px solid var(--line)",
        background: "transparent",
        color: "var(--fg-3)",
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.18em",
        textTransform: "uppercase",
        cursor: busy ? "wait" : "pointer",
      }}
    >
      {busy ? "saving…" : "⬡ save plan → actions"}
    </button>
  );
}
