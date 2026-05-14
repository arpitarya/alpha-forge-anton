"use client";

import { Logo } from "@alphaforge/solar-orb-ui";
import { useEffect, useRef, useState } from "react";

interface Step {
  key: string;
  label: string;
  doneStatus: string;
}

const STEPS: Step[] = [
  { key: "backend",  label: "backend · fastapi on :8000",          doneStatus: "142ms"  },
  { key: "postgres", label: "postgres · 16 ready",                  doneStatus: "08ms"   },
  { key: "redis",    label: "redis · pubsub connected",             doneStatus: "04ms"   },
  { key: "kite",     label: "zerodha · kite session",               doneStatus: "synced" },
  { key: "llm",      label: "llm gateway · gemini / groq / local",  doneStatus: "ready"  },
  { key: "screener", label: "screener · loading cached features",   doneStatus: "ready"  },
  { key: "ticks",    label: "watchlist · streaming ticks",          doneStatus: "ready"  },
];

const NOW_STATUS: Record<string, string> = {
  kite:     "syncing 12 positions…",
  llm:      "benchmarking providers",
  screener: "loading cached features",
  ticks:    "streaming ticks…",
};

const HEADLINES: Record<string, string> = {
  backend:  "Give me a second — I'm spinning up your terminal.",
  postgres: "Connecting to your data.",
  redis:    "Wiring up the live feed.",
  kite:     "Pulling your Zerodha positions…",
  llm:      "Picking the best LLM for the job.",
  screener: "Loading screener features.",
  ticks:    "Almost ready — streaming ticks.",
  done:     "Welcome back, Arpit.",
};

export interface BootScreenProps {
  onDone: () => void;
  exiting?: boolean;
}

export function BootScreen({ onDone, exiting = false }: BootScreenProps) {
  const [done, setDone] = useState(3);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    let step = 3;
    let t: ReturnType<typeof setTimeout>;

    function next() {
      step += 1;
      setDone(step);
      if (step < STEPS.length) {
        t = setTimeout(next, 700 + Math.random() * 500);
      } else {
        t = setTimeout(() => onDoneRef.current(), 650);
      }
    }

    t = setTimeout(next, 900);
    return () => clearTimeout(t);
  }, []);

  const pct = Math.round((done / STEPS.length) * 100);
  const currentKey = done < STEPS.length ? STEPS[done].key : "done";
  const headline = HEADLINES[currentKey] ?? HEADLINES.done;
  const allDone = done >= STEPS.length;

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
          <br />VER_0.9.4.ALPHA
        </span>
        <span
          aria-hidden
          className="absolute right-6 top-6 text-right font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-in 0.7s 0.25s ease-out both" }}
        >
          <span className="text-[color:var(--accent)]">LATENCY · 8ms</span>
          <br />UPLINK_STABLE ⦾
        </span>
        <span
          aria-hidden
          className="absolute bottom-6 left-6 font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-bl-in 0.7s 0.3s ease-out both" }}
        >
          MEMORY_ALLOCATION
          <br /><span className="text-[color:var(--accent)]">128.00 GB</span>
        </span>
        <span
          aria-hidden
          className="absolute bottom-6 right-6 text-right font-mono text-[11px] leading-relaxed tracking-[0.18em] uppercase text-[color:var(--fg-3)]"
          style={{ animation: "boot-corner-bl-in 0.7s 0.2s ease-out both" }}
        >
          GEOLOCATION
          <br /><span className="text-[color:var(--accent)]">NODE_MUMBAI_01</span>
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
            {STEPS.map((s, idx) => {
              const isOk  = idx < done;
              const isNow = idx === done;
              const status = isOk
                ? s.doneStatus
                : isNow
                ? (NOW_STATUS[s.key] ?? "…")
                : "queued";
              const glyph = isOk ? "✓" : isNow ? "◐" : "○";

              return (
                <li
                  key={s.key}
                  className="grid items-center gap-3.5 font-mono text-[12.5px]"
                  style={{
                    gridTemplateColumns: "18px 1fr auto",
                    animation: `boot-row-in 0.4s ${0.05 + idx * 0.055}s cubic-bezier(0.2,0,0,1) both`,
                    transition: "color 0.35s ease, opacity 0.35s ease",
                    opacity: !isOk && !isNow ? 0.45 : 1,
                  }}
                >
                  <span
                    className="grid h-[18px] w-[18px] place-items-center text-sm"
                    style={{
                      color: isOk ? "var(--green)" : isNow ? "var(--accent)" : "var(--fg-4)",
                      transition: "color 0.35s ease",
                      animation: isNow ? "boot-step-spin 1.4s linear infinite" : undefined,
                    }}
                  >
                    {glyph}
                  </span>
                  <span
                    style={{
                      color: isOk || isNow ? "var(--fg)" : "var(--fg-3)",
                      transition: "color 0.35s ease",
                    }}
                  >
                    {s.label}
                  </span>
                  <span
                    className="text-[11px] uppercase tracking-[0.18em]"
                    style={{
                      color: isNow ? "var(--accent)" : isOk ? "var(--fg-3)" : "var(--fg-4)",
                      transition: "color 0.35s ease",
                    }}
                  >
                    {status}
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
                background: "linear-gradient(90deg, var(--accent-dim), var(--accent), var(--accent-soft))",
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
            <span>{done} of {STEPS.length} services online</span>
            <span
              style={{
                color: allDone ? "var(--green)" : "var(--accent)",
                animation: allDone ? "boot-ready-in 0.45s cubic-bezier(0.2,0,0,1) both" : undefined,
                transition: "color 0.4s ease",
              }}
            >
              {allDone ? "● READY" : `~${((STEPS.length - done) * 0.8).toFixed(1)}s remaining`}
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
