"use client";

import { Logo } from "@alphaforge-anton/solar-ui";
import { useEffect, useRef, useState } from "react";
import type { BootStatus } from "./boot.types";

export interface BootStep {
  key: string;
  label: string;
  /** Final status of this system once the probe completes. */
  status: BootStatus;
  /** Short status text rendered on the right (e.g. "ready", "12ms", "not linked"). */
  doneStatus: string;
}

/** Static fallback used only if the live probe call fails. Real boot rows
 * come from `GET /api/v1/health/boot` via `BootGate`. */
export const BOOT_STEPS: BootStep[] = [
  { key: "backend", label: "Backend · FastAPI gateway", status: "ok", doneStatus: "online" },
  { key: "database", label: "Database · Postgres ready", status: "ok", doneStatus: "ready" },
  { key: "llm", label: "AI Gateway · LLM routing", status: "warn", doneStatus: "no key" },
  {
    key: "zerodha",
    label: "Zerodha (Kite) · holdings source",
    status: "warn",
    doneStatus: "not linked",
  },
  { key: "groww", label: "Groww · holdings source", status: "warn", doneStatus: "not linked" },
  {
    key: "wintwealth",
    label: "Wint Wealth · holdings source",
    status: "warn",
    doneStatus: "not linked",
  },
  {
    key: "angelone",
    label: "Angel One · holdings source",
    status: "warn",
    doneStatus: "not linked",
  },
];

const NOW_STATUS: Record<string, string> = {
  database: "querying postgres…",
  llm: "connecting to AI providers…",
  zerodha: "syncing Zerodha positions…",
  groww: "syncing Groww holdings…",
  wintwealth: "syncing bonds & SGBs…",
  angelone: "syncing Angel One snapshot…",
  indmoney: "syncing IndMoney holdings…",
  tickertape: "syncing Tickertape data…",
};

const HEADLINES: Record<string, string> = {
  backend: "Give me a second — I'm spinning up your terminal.",
  database: "Connecting to your data.",
  llm: "Wiring up your AI analyst…",
  zerodha: "Pulling your Zerodha positions…",
  groww: "Loading your Groww book…",
  wintwealth: "Reading Wint Wealth bonds & SGBs…",
  angelone: "Refreshing your Angel One snapshot…",
  done: "Welcome back, Arpit.",
};

export interface BootScreenProps {
  /** Service checklist rendered + animated through. Defaults to `BOOT_STEPS`. */
  steps?: BootStep[];
  onDone: () => void;
  exiting?: boolean;
  /** Gate: navigation is held until sync resolves. Animation still plays immediately. */
  syncReady?: boolean;
  /** When true, each row is shown immediately with its declared status (no
   * timer-driven reveal). Used by BootGate when /health/boot is the source of
   * truth so the splash mirrors actual probe state instead of a fake progress. */
  live?: boolean;
}

export function BootScreen({
  steps = BOOT_STEPS,
  onDone,
  exiting = false,
  syncReady = false,
  live = false,
}: BootScreenProps) {
  // In live mode every row is "done" the moment we have probe data; the row's
  // colour/glyph already encodes whether it's OK or blocking. In demo mode we
  // keep the staggered reveal so the splash feels alive even with no data.
  const [done, setDone] = useState(live ? steps.length : 3);
  const [animDone, setAnimDone] = useState(live);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  // Fire onDone only when both animation and sync have settled.
  useEffect(() => {
    if (animDone && syncReady) onDoneRef.current();
  }, [animDone, syncReady]);

  // Keep `done` synced with the live step count so newly-arriving probe rows
  // appear immediately rather than waiting for a timer.
  useEffect(() => {
    if (!live) return;
    setDone(steps.length);
    setAnimDone(true);
  }, [live, steps.length]);

  useEffect(() => {
    if (live) return;
    let step = 3;
    let t: ReturnType<typeof setTimeout>;

    function next() {
      step += 1;
      setDone(step);
      if (step < steps.length) {
        t = setTimeout(next, 700 + Math.random() * 500);
      } else {
        t = setTimeout(() => setAnimDone(true), 650);
      }
    }

    t = setTimeout(next, 900);
    return () => clearTimeout(t);
  }, [steps.length, live]);

  // In live mode the meaningful progress is "OK probes / total probes" rather
  // than "rows revealed / total rows" (which would always be 100%).
  const okCount = steps.filter((s) => s.status === "ok").length;
  const pct = live
    ? Math.round((okCount / Math.max(steps.length, 1)) * 100)
    : Math.round((done / steps.length) * 100);
  const firstBlocker = live
    ? steps.find((s) => s.status === "error" || s.status === "warn")
    : undefined;
  const currentKey = live
    ? syncReady
      ? "done"
      : (firstBlocker?.key ?? "backend")
    : done < steps.length
      ? steps[done].key
      : "done";
  const headline =
    live && firstBlocker?.key === "vault"
      ? "Vault is locked — run `afbach unlock` to continue."
      : (HEADLINES[currentKey] ?? HEADLINES.done);
  const allDone = live ? syncReady : done >= steps.length;

  return (
    <>
      <style>{`
        @keyframes boot-screen-in {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes boot-screen-out {
          from { opacity: 1; transform: scale(1); }
          to   { opacity: 0; transform: scale(1.015); }
        }
        @keyframes boot-content-up {
          from { opacity: 0; transform: translateY(14px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes boot-corner-in {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes boot-corner-bl-in {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes boot-headline-in {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes boot-logo-breathe {
          0%, 100% { transform: scale(1);    opacity: 1; }
          50%      { transform: scale(1.04); opacity: 0.9; }
        }
        @keyframes boot-step-spin {
          to { transform: rotate(1turn); }
        }
        @keyframes boot-row-in {
          from { opacity: 0; transform: translateX(-8px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes boot-bar-pulse {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0.55; }
        }
        @keyframes boot-ready-in {
          from { opacity: 0; letter-spacing: 0.4em; }
          to   { opacity: 1; letter-spacing: 0.2em; }
        }
      `}</style>

      <div
        className="relative flex h-screen w-screen flex-col items-center justify-center overflow-hidden"
        style={{
          background:
            "radial-gradient(900px 600px at 50% 40%, var(--glow), transparent 70%), var(--bg)",
          animation: exiting
            ? "boot-screen-out 0.45s cubic-bezier(0.4, 0, 1, 1) both"
            : "boot-screen-in 0.5s ease-out both",
        }}
      >
        {/* Dot grid */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-[0.055]"
          style={{
            backgroundImage:
              "repeating-linear-gradient(0deg, transparent 0 47px, var(--line-hi) 47px 48px), repeating-linear-gradient(90deg, transparent 0 47px, var(--line-hi) 47px 48px)",
          }}
        />

        {/* Corner labels */}
        <span
          aria-hidden
          className="absolute left-6 top-6 font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-in 0.7s 0.15s ease-out both" }}
        >
          <span className="text-[color:var(--accent)]">SYSTEM.CORE.KERNEL</span>
          <br />
          VER_0.9.4.ALPHA
        </span>
        <span
          aria-hidden
          className="absolute right-6 top-6 text-right font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-in 0.7s 0.25s ease-out both" }}
        >
          <span className="text-[color:var(--accent)]">LATENCY · 8ms</span>
          <br />
          UPLINK_STABLE ⦾
        </span>
        <span
          aria-hidden
          className="absolute bottom-6 left-6 font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-bl-in 0.7s 0.3s ease-out both" }}
        >
          MEMORY_ALLOCATION
          <br />
          <span className="text-[color:var(--accent)]">128.00 GB</span>
        </span>
        <span
          aria-hidden
          className="absolute bottom-6 right-6 text-right font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-bl-in 0.7s 0.2s ease-out both" }}
        >
          GEOLOCATION
          <br />
          <span className="text-[color:var(--accent)]">NODE_MUMBAI_01</span>
        </span>

        {/* Main column */}
        <div
          className="relative z-10 w-[620px] max-w-[90vw]"
          style={{ animation: "boot-content-up 0.65s 0.1s cubic-bezier(0.2, 0, 0, 1) both" }}
        >
          {/* Logo */}
          <div
            className="mb-5 w-24"
            style={{
              filter: "drop-shadow(0 0 28px var(--glow)) drop-shadow(0 0 56px var(--glow))",
              animation: "boot-logo-breathe 3.4s 0.3s ease-in-out infinite",
            }}
          >
            <Logo variant="icon" size="xl" />
          </div>

          <p className="font-mono text-[10px] tracking-[0.3em] uppercase text-[color:var(--accent)]">
            · WARMING UP
          </p>

          {/* Headline — re-keyed on each step so it re-animates */}
          <h1
            key={currentKey}
            className="mt-1.5 text-[38px] font-[500] leading-[1.05] tracking-[-0.02em]"
            style={{ animation: "boot-headline-in 0.38s cubic-bezier(0.2, 0, 0, 1) both" }}
          >
            {headline}
          </h1>

          <hr className="my-5 border-0 border-t border-[color:var(--line-hi)]" />

          {/* Service rows */}
          <ul className="flex flex-col gap-3">
            {steps.map((s, idx) => {
              const isDone = idx < done;
              const isNow = idx === done;
              type RowState = BootStatus | "pending" | "queued";
              const probeStatus: RowState = isDone ? s.status : isNow ? "pending" : "queued";
              const detail = isDone ? s.doneStatus : isNow ? (NOW_STATUS[s.key] ?? "…") : "queued";
              const glyph =
                probeStatus === "ok"
                  ? "✓"
                  : probeStatus === "warn"
                    ? "!"
                    : probeStatus === "error"
                      ? "✗"
                      : probeStatus === "pending"
                        ? "◐"
                        : "○";
              const glyphColor =
                probeStatus === "ok"
                  ? "var(--green)"
                  : probeStatus === "warn"
                    ? "var(--accent)"
                    : probeStatus === "error"
                      ? "var(--red)"
                      : probeStatus === "pending"
                        ? "var(--accent)"
                        : "var(--fg-4)";
              const detailColor =
                probeStatus === "warn"
                  ? "var(--accent)"
                  : probeStatus === "error"
                    ? "var(--red)"
                    : isNow
                      ? "var(--accent)"
                      : isDone
                        ? "var(--fg-3)"
                        : "var(--fg-4)";

              return (
                <li
                  key={s.key}
                  className="grid items-center gap-3.5 font-mono text-[12.5px]"
                  style={{
                    gridTemplateColumns: "18px 1fr auto",
                    animation: `boot-row-in 0.4s ${0.05 + idx * 0.055}s cubic-bezier(0.2,0,0,1) both`,
                    transition: "color 0.35s ease, opacity 0.35s ease",
                    opacity: !isDone && !isNow ? 0.45 : 1,
                  }}
                >
                  <span
                    className="grid h-[18px] w-[18px] place-items-center text-sm"
                    style={{
                      color: glyphColor,
                      transition: "color 0.35s ease",
                      animation:
                        probeStatus === "pending"
                          ? "boot-step-spin 1.4s linear infinite"
                          : undefined,
                    }}
                  >
                    {glyph}
                  </span>
                  <span
                    style={{
                      color: isDone || isNow ? "var(--fg)" : "var(--fg-3)",
                      transition: "color 0.35s ease",
                    }}
                  >
                    {s.label}
                  </span>
                  <span
                    className="text-[11px] uppercase tracking-[0.18em]"
                    style={{ color: detailColor, transition: "color 0.35s ease" }}
                  >
                    {detail}
                  </span>
                </li>
              );
            })}
          </ul>

          {/* Progress bar */}
          <div className="relative mt-6 h-[3px] overflow-hidden rounded-full bg-[color:var(--line-hi)]">
            <div
              className="h-full rounded-full"
              style={{
                width: `${pct}%`,
                background:
                  "linear-gradient(90deg, var(--accent-dim), var(--accent), var(--accent-soft))",
                boxShadow: "0 0 12px var(--glow), 0 0 28px var(--glow)",
                transition: "width 0.75s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            />
            {/* Moving glow dot at leading edge */}
            {!allDone && (
              <div
                aria-hidden
                className="absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full"
                style={{
                  left: `calc(${pct}% - 8px)`,
                  background: "var(--accent-soft)",
                  filter: "blur(6px)",
                  opacity: 0.8,
                  transition: "left 0.75s cubic-bezier(0.4, 0, 0.2, 1)",
                  animation: "boot-bar-pulse 1.2s ease-in-out infinite",
                }}
              />
            )}
          </div>

          <div className="mt-2 flex justify-between font-mono text-[10px] tracking-[0.2em] uppercase text-[color:var(--fg-3)]">
            <span>
              {done} of {steps.length} systems ready
            </span>
            <span
              style={{
                color: allDone ? "var(--green)" : "var(--accent)",
                animation: allDone ? "boot-ready-in 0.45s cubic-bezier(0.2,0,0,1) both" : undefined,
                transition: "color 0.4s ease",
              }}
            >
              {allDone ? "● READY" : `~${((steps.length - done) * 0.8).toFixed(1)}s remaining`}
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
