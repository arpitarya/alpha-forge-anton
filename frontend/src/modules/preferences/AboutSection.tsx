"use client";

import { PrefGroup } from "./PrefGroup";
import { PrefRow } from "./PrefRow";

function StaticBox({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-[6px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] px-3 py-2 font-mono text-[12px] tracking-[0.04em] text-[color:var(--fg)]">
      {children}
    </span>
  );
}

export function AboutSection() {
  return (
    <PrefGroup num="01" title="Alpha Forge" meta="v0.9.4 · alpha">
      <PrefRow
        name="Build"
        desc="Latest deploy to your terminal."
        control={<StaticBox>0.9.4-alpha · 2026-05-12</StaticBox>}
        tail={<b className="font-normal text-[color:var(--accent)]">Stable</b>}
      />
      <PrefRow
        name="Backend"
        desc="FastAPI on :8000"
        control={<StaticBox>node_mumbai_01 · 8ms</StaticBox>}
        tail={<b className="font-normal text-[color:var(--accent)]">Online</b>}
      />
      <PrefRow
        name="License"
        control={<StaticBox>Pro — seat #00142</StaticBox>}
        tail={<b className="font-normal text-[color:var(--accent)]">Valid</b>}
      />
      <PrefRow
        name="Documentation"
        control={
          <a
            href="#"
            onClick={(e) => e.preventDefault()}
            className="rounded-[5px] border border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)]"
          >
            Open docs →
          </a>
        }
      />
      <PrefRow
        name="Reset all preferences"
        desc="Restores every setting on this page to its default. Account and broker connections are kept."
        control={
          <button
            type="button"
            className="rounded-[6px] border border-[color:color-mix(in_srgb,var(--red)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--red)_8%,transparent)] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--red)] transition hover:bg-[color:color-mix(in_srgb,var(--red)_16%,transparent)]"
          >
            Reset preferences
          </button>
        }
      />
    </PrefGroup>
  );
}
