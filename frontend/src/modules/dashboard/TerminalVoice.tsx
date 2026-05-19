"use client";

import {
  Button,
  MicIndicator,
  Text,
  VoiceDock,
  Waveform,
} from "@alphaforge-anton/ravel-ui";
import { useEffect, useState } from "react";

const PROMPTS = [
  '"Alpha, analyze my exposure to AI stocks"',
  '"Show banking drag this week"',
  '"Rebalance equity down 5% to target"',
  '"Screener: breakouts under ₹500"',
];

export function TerminalVoice() {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % PROMPTS.length), 3800);
    return () => clearInterval(id);
  }, []);

  return (
    <VoiceDock
      mic={<MicIndicator size={28} active />}
      center={
        <>
          <div className="flex flex-none items-center gap-2">
            <Text className="text-[12px] font-medium italic leading-none text-[color:var(--accent)]">
              Listening…
            </Text>
            <Text variant="tag" tone="subtle" className="text-[9px] tracking-[0.22em]">
              · Neural Interface
            </Text>
          </div>
          <Waveform bars={8} height={16} />
          <Text className="ml-1 flex-1 truncate text-[12px] italic leading-none text-[color:var(--fg-2)]">
            {PROMPTS[idx]}
          </Text>
        </>
      }
      cta={
        <Button variant="deploy" size="sm" className="rounded-[6px] px-3.5 py-1.5 text-[10px] tracking-[0.22em]">
          Deploy ▸
        </Button>
      }
    />
  );
}
