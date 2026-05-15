"use client";

import { usePathname } from "next/navigation";
import { type ReactNode, useCallback, useEffect, useState } from "react";
import { fetchBootReport } from "./boot.api";
import type { BootService } from "./boot.types";
import { BOOT_STEPS, type BootStep, BootScreen } from "./BootScreen";

type Phase = "boot" | "exiting" | "done";

const FADE_OUT_MS = 450; // must match boot-screen-out animation duration
const SESSION_KEY = "af-booted";

function toStep(s: BootService): BootStep {
  return { key: s.key, label: s.label, status: s.status, doneStatus: s.detail };
}

export function BootGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const skip = pathname === "/login";

  const [phase, setPhase] = useState<Phase>("done");
  const [hydrated, setHydrated] = useState(false);
  const [steps, setSteps] = useState<BootStep[]>(BOOT_STEPS);

  useEffect(() => {
    if (skip) {
      setPhase("done");
      setHydrated(true);
      return;
    }
    const booted = typeof window !== "undefined" && sessionStorage.getItem(SESSION_KEY) === "1";
    if (booted) {
      setPhase("done");
      setHydrated(true);
      return;
    }
    // Real probe: fetch live system snapshot. If it fails the static fallback
    // in BOOT_STEPS still produces a usable splash.
    fetchBootReport()
      .then((r) => setSteps(r.services.map(toStep)))
      .catch(() => { /* fallback already in state */ })
      .finally(() => {
        setPhase("boot");
        setHydrated(true);
      });
  }, [skip]);

  const handleDone = useCallback(() => {
    setPhase("exiting");
    setTimeout(() => {
      sessionStorage.setItem(SESSION_KEY, "1");
      setPhase("done");
    }, FADE_OUT_MS);
  }, []);

  if (!hydrated) return null;

  if (phase === "done") {
    return (
      <>
        <style>{`
          @keyframes boot-app-in {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
          }
        `}</style>
        <div style={{ animation: "boot-app-in 0.5s cubic-bezier(0.2, 0, 0, 1) both" }}>
          {children}
        </div>
      </>
    );
  }

  return <BootScreen steps={steps} onDone={handleDone} exiting={phase === "exiting"} />;
}
