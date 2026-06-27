import type { ReactNode } from "react";

export type ChipTone = "acc" | "warn" | "bad";

/** One badge scale across the integrated Hi-Fi: acc = live/confident, warn =
 * caution (dashed), bad = danger. Replaces the three bespoke per-surface tags. */
export function UChip({
  tone = "acc",
  dashed,
  children,
}: {
  tone?: ChipTone;
  dashed?: boolean;
  children: ReactNode;
}) {
  return (
    <span className={`of-chip ${tone}`} style={dashed ? { borderStyle: "dashed" } : undefined}>
      {children}
    </span>
  );
}
