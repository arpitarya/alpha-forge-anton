import type { CSSProperties } from "react";

export const styles = {
  btn: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    height: 24,
    padding: "0 8px 0 9px",
    maxWidth: 280,
    background: "color-mix(in srgb, var(--surface-lo) 70%, transparent)",
    border: "1px solid var(--line)",
    borderRadius: 6,
    color: "var(--fg-2)",
    cursor: "pointer",
    fontFamily: "Space Grotesk, sans-serif",
    transition: "all .15s",
  } satisfies CSSProperties,

  dot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    flexShrink: 0,
    background: "var(--accent)",
    boxShadow: "0 0 8px var(--glow)",
    animation: "mdlPulse 2.4s ease-in-out infinite",
  } satisfies CSSProperties,

  menu: {
    position: "fixed",
    width: 560,
    display: "flex",
    flexDirection: "column",
    background: "color-mix(in srgb, var(--surface) 96%, transparent)",
    border: "1px solid var(--line-hi)",
    borderRadius: 10,
    boxShadow:
      "0 18px 60px -10px rgba(0,0,0,.65), 0 0 0 1px color-mix(in srgb, var(--accent) 8%, transparent)",
    backdropFilter: "blur(18px)",
    zIndex: 9999,
    overflow: "hidden",
    transformOrigin: "bottom right",
  } satisfies CSSProperties,

  grid: {
    display: "grid",
    gridTemplateColumns: "206px 1fr",
    flex: 1,
    minHeight: 0,
    overflow: "hidden",
  } satisfies CSSProperties,

  col: {
    display: "flex",
    flexDirection: "column",
    minWidth: 0,
  } satisfies CSSProperties,

  colDivider: {
    borderLeft: "1px solid var(--line)",
  } satisfies CSSProperties,

  colHead: {
    fontFamily: "Space Mono, monospace",
    fontSize: 9,
    letterSpacing: "0.24em",
    color: "var(--fg-4)",
    padding: "11px 13px 8px",
    textTransform: "uppercase",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    gap: 6,
    flexShrink: 0,
  } satisfies CSSProperties,

  colBody: {
    padding: "0 6px 6px",
    overflowY: "auto",
    maxHeight: 420,
    flex: 1,
    minHeight: 0,
  } satisfies CSSProperties,

  foot: {
    borderTop: "1px solid var(--line)",
    padding: "9px 13px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontFamily: "Space Mono, monospace",
    fontSize: 9.5,
    letterSpacing: "0.1em",
    color: "var(--fg-3)",
    background: "color-mix(in srgb, var(--surface-lo) 40%, transparent)",
    flexShrink: 0,
  } satisfies CSSProperties,
};
