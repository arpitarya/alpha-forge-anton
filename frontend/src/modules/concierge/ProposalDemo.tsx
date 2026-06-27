"use client";

import { useState } from "react";
import { ConeCard } from "./ConeCard";
import { FeedToggle } from "./FeedToggle";
import { type Feed, GroundedAnswer } from "./GroundedAnswer";
import { ProposalCard } from "./ProposalCard";
import { PROPOSAL_DEMO } from "./proposal.mock";

/**
 * The integrated-Hi-Fi demo turn, rendered inline in the chat thread on MOCK data
 * (triggered by the `/proposal` command — no API). One grounded Orff answer that
 * carries the cone + the downside-first proposal, with a LIVE/STALE/ERROR feed
 * switch and a cone-confidence switch so every honest-pending state is reachable.
 */
export function ProposalDemo() {
  const [feed, setFeed] = useState<Feed>("live");
  const [low, setLow] = useState(false);

  return (
    <div data-proposal-demo style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div className="of-msg">
        <div className="of-orb" />
        <div className="of-bubble">
          <div className="lead">
            Should I sell premium into Thursday's RBI decision?{" "}
            <b>Here's the red-teamed case — downside first.</b>
          </div>

          <div style={{ marginTop: 12 }}>
            <FeedToggle value={feed} onChange={setFeed} />
            {feed === "live" && <ConfTog low={low} onChange={setLow} />}
          </div>

          <GroundedAnswer feed={feed} />

          {feed !== "error" && (
            <>
              <div className="of-sub">90-day outcome cone</div>
              <ConeCard low={low} stale={feed === "stale"} />
            </>
          )}

          {feed !== "error" && (
            <div style={{ marginTop: 14 }}>
              <ProposalCard p={PROPOSAL_DEMO} feedStale={feed === "stale"} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ConfTog({ low, onChange }: { low: boolean; onChange: (v: boolean) => void }) {
  const opt = (v: boolean, label: string, warn?: boolean) => {
    const on = low === v;
    const color = warn ? "var(--accent-soft)" : "var(--accent)";
    return (
      <button
        type="button"
        onClick={() => onChange(v)}
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: ".12em",
          textTransform: "uppercase",
          padding: "4px 9px",
          borderRadius: 5,
          cursor: "pointer",
          color: on ? color : "var(--fg-3)",
          background: on ? `color-mix(in srgb, ${color} 8%, transparent)` : "transparent",
          border: `1px solid ${on ? `color-mix(in srgb, ${color} 45%, transparent)` : "var(--line-hi)"}`,
        }}
      >
        {label}
      </button>
    );
  };
  return (
    <div
      style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12, flexWrap: "wrap" }}
    >
      <span
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: ".16em",
          textTransform: "uppercase",
          color: "var(--fg-3)",
          marginRight: 2,
        }}
      >
        cone
      </span>
      {opt(false, "confident")}
      {opt(true, "low-confidence", true)}
    </div>
  );
}
