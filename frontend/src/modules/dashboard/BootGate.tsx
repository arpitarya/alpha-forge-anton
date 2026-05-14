"use client";

import { type ReactNode, useCallback, useState } from "react";
import { BootScreen } from "./BootScreen";

type Phase = "boot" | "exiting" | "done";

const FADE_OUT_MS = 450; // must match boot-screen-out animation duration

export function BootGate({ children }: { children: ReactNode }) {
  const [phase, setPhase] = useState<Phase>("boot");

  const handleDone = useCallback(() => {
    setPhase("exiting");
    setTimeout(() => setPhase("done"), FADE_OUT_MS);
  }, []);

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

  return <BootScreen onDone={handleDone} exiting={phase === "exiting"} />;
}
