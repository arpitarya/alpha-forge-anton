"use client";

import { Disclosure } from "./Disclosure";

/**
 * Orff's reasoning trace, split server-side from a `<think>` block on reasoning
 * models — surfaced collapsed (open while streaming, before the answer lands).
 */
export function ThinkingBlock({ text, streaming }: { text: string; streaming: boolean }) {
  if (!text) return null;
  return (
    <Disclosure label="Orff's reasoning" tone="accent" defaultOpen={streaming}>
      <div
        style={{
          paddingTop: 6,
          fontFamily: "Space Grotesk, sans-serif",
          fontSize: 12,
          lineHeight: 1.6,
          color: "var(--fg-3)",
          whiteSpace: "pre-wrap",
          fontStyle: "italic",
        }}
      >
        {text}
      </div>
    </Disclosure>
  );
}
