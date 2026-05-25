"use client";

import { PrefInput } from "@alphaforge-anton/solar-ui";
import { PrefGroup } from "@alphaforge-anton/solar-ui";
import { PrefRow } from "@alphaforge-anton/solar-ui";
import type { PrefDraft } from "./usePrefStore";

export interface AccountSectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

const BROKERS: Array<{
  short: string;
  name: string;
  sub: string;
  cls: string;
  connected: boolean;
  cta: string;
}> = [
  { short: "KT", name: "Zerodha · Kite", sub: "Equity · F&O · MF · 12 positions synced",     cls: "from-[#f17545] to-[#d24316]",            connected: true,  cta: "Manage" },
  { short: "CB", name: "Coinbase",       sub: "Crypto · 4 holdings",                          cls: "from-[#3b6eea] to-[#1146c4]",            connected: true,  cta: "Manage" },
  { short: "FY", name: "Fyers",          sub: "Not connected",                                cls: "from-[#3f3f3f] to-[#161616]",            connected: false, cta: "Connect" },
];

export function AccountSection({ t, setTweak }: AccountSectionProps) {
  const initial = (t.userName || "A").trim().charAt(0).toUpperCase();
  return (
    <>
      <PrefGroup num="01" title="Profile" meta="Pro · since Apr 2024">
        <div
          className="grid items-center gap-5 border-b border-[color:var(--line)] pb-5 pt-1"
          style={{ gridTemplateColumns: "84px 1fr auto" }}
        >
          <div
            className="acct-avatar relative grid h-[84px] w-[84px] place-items-center rounded-full text-[34px] font-semibold tracking-[-0.02em] text-[color:var(--on-accent)]"
            style={{
              background:
                "radial-gradient(circle at 30% 30%, #fff, var(--accent-soft) 18%, var(--accent) 60%, var(--accent-dim))",
              boxShadow:
                "0 0 32px var(--glow), inset -8px -10px 18px color-mix(in srgb, var(--accent-dim) 50%, transparent), inset 6px 6px 16px rgba(255,255,255,.4)",
            }}
          >
            {initial}
          </div>
          <div>
            <div className="text-[22px] font-medium tracking-[-0.01em]">{t.userName || "Trader"}</div>
            <div className="mt-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
              <b className="font-normal text-[color:var(--accent)]">arjun.k@protonmail.com</b>
              <span className="mx-2 inline-block h-1 w-1 rounded-full bg-[color:var(--fg-4)] align-middle" />
              NODE_MUMBAI_01
              <span className="mx-2 inline-block h-1 w-1 rounded-full bg-[color:var(--fg-4)] align-middle" />
              2FA ON
            </div>
          </div>
          <span className="rounded-[4px] border border-[color:color-mix(in_srgb,var(--accent)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_16%,transparent)] px-3.5 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.24em] text-[color:var(--accent)]">
            ★ Pro
          </span>
        </div>
        <PrefRow
          name="Display name"
          desc="Shown in the top bar and on Alpha's spoken replies."
          control={<PrefInput value={t.userName} onChange={(v) => setTweak("userName", v)} />}
        />
        <PrefRow
          name="Status label"
          desc="The tagline next to the live dot in the top bar."
          control={<PrefInput value={t.statusLabel} onChange={(v) => setTweak("statusLabel", v)} />}
        />
      </PrefGroup>

      <PrefGroup num="02" title="Connected brokers">
        <div className="flex flex-col">
          {BROKERS.map((b) => (
            <div
              key={b.short}
              className="grid items-center gap-3.5 border-b border-[color:var(--line)] py-3 last:border-b-0"
              style={{ gridTemplateColumns: "36px 1fr auto auto" }}
            >
              <div
                className={`grid h-9 w-9 place-items-center rounded-[8px] bg-gradient-to-br ${b.cls} font-mono text-[10px] font-bold tracking-[0.06em] text-white`}
              >
                {b.short}
              </div>
              <div>
                <div className="text-[13px] font-medium">{b.name}</div>
                <div className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
                  {b.sub}
                </div>
              </div>
              <span
                className={`inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.18em] ${
                  b.connected ? "text-[color:var(--green)]" : "text-[color:var(--fg-3)]"
                }`}
              >
                <span
                  className="h-1.5 w-1.5 rounded-full bg-current"
                  style={{ boxShadow: "0 0 6px currentColor" }}
                />
                {b.connected ? "Connected" : "Idle"}
              </span>
              <button
                type="button"
                className={`rounded-[5px] border px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] transition ${
                  b.connected
                    ? "border-[color:var(--line-hi)] text-[color:var(--fg-3)] hover:border-[color:var(--fg-3)] hover:text-[color:var(--fg)]"
                    : "border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)]"
                }`}
              >
                {b.cta}
              </button>
            </div>
          ))}
        </div>
      </PrefGroup>

      <PrefGroup num="03" title="Hotkeys">
        <Hotkey label="Command palette" keys={["⌘", "K"]} />
        <Hotkey label="Toggle terminal" keys={["⌘", "1"]} />
        <Hotkey label="Toggle portfolio" keys={["⌘", "2"]} />
        <Hotkey label="Open preferences" keys={["⌘", ","]} />
        <Hotkey label="Activate Alpha voice" keys={["Space"]} extra="(hold)" />
      </PrefGroup>
    </>
  );
}

function Hotkey({ label, keys, extra }: { label: string; keys: string[]; extra?: string }) {
  return (
    <PrefRow
      name={label}
      control={
        <div className="flex items-center gap-1">
          {keys.map((k, i) => (
            <span key={k}>
              <span className="rounded-[4px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] px-1.5 py-0.5 font-mono text-[10px] text-[color:var(--fg-2)]">
                {k}
              </span>
              {i < keys.length - 1 && (
                <span className="mx-1 font-mono text-[10px] text-[color:var(--fg-3)]">+</span>
              )}
            </span>
          ))}
          {extra && <span className="ml-2 font-mono text-[10px] text-[color:var(--fg-3)]">{extra}</span>}
        </div>
      }
    />
  );
}
