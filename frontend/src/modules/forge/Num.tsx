import type { CSSProperties } from "react";

export type NumKind = "loss" | "gain" | "neutral";

/**
 * Downside-first money — Space Mono, tabular, Indian grouping at the call site.
 * Worst-case is shown first and loudest; `glow` adds the red/green halo the
 * Hi-Fi uses on the Expected-Shortfall hero and the acknowledged figure.
 */
export function Num({
  v,
  kind = "neutral",
  big,
  glow,
  className = "",
}: {
  v: string;
  kind?: NumKind;
  big?: number | string;
  glow?: boolean;
  className?: string;
}) {
  const style: CSSProperties = {};
  if (big) {
    style.fontSize = big;
    style.fontWeight = 600;
    style.letterSpacing = "-.02em";
    style.lineHeight = 1;
  }
  if (glow && kind === "loss")
    style.textShadow = "0 0 30px color-mix(in srgb, var(--red) 35%, transparent)";
  if (glow && kind === "gain")
    style.textShadow = "0 0 30px color-mix(in srgb, var(--green) 30%, transparent)";
  return (
    <span className={`of-num ${kind} ${className}`.trim()} style={style}>
      {v}
    </span>
  );
}
