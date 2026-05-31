"use client";

import type { ModelMeta, ProviderMeta } from "./concierge.providers";

interface AutoRowProps {
  title: string;
  desc: string;
  arrow: string;
  selected: boolean;
  onClick: () => void;
}

export function AutoRow({ title, desc, arrow, selected, onClick }: AutoRowProps) {
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 9,
        width: "100%",
        padding: "9px 10px",
        border: `1px ${selected ? "solid" : "dashed"} color-mix(in srgb, var(--accent) ${selected ? 60 : 30}%, transparent)`,
        background: `color-mix(in srgb, var(--accent) ${selected ? 14 : 6}%, transparent)`,
        borderRadius: 6,
        cursor: "pointer",
        textAlign: "left",
        color: "var(--accent)",
        fontFamily: "Space Grotesk, sans-serif",
        marginBottom: 6,
        transition: "all .12s",
      }}
    >
      <span style={glyphStyle}>★</span>
      <span style={{ display: "flex", flexDirection: "column", gap: 2, flex: 1, minWidth: 0 }}>
        <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--accent)" }}>{title}</span>
        <span style={{ fontSize: 10.5, color: "var(--fg-2)", lineHeight: 1.3 }}>{desc}</span>
      </span>
      <span style={arrowStyle}>{arrow}</span>
    </button>
  );
}

interface ProvRowProps {
  p: ProviderMeta;
  focused: boolean;
  hasSelection: boolean;
  onHover: () => void;
  onClick: () => void;
}

export function ProvRow({ p, focused, hasSelection, onHover, onClick }: ProvRowProps) {
  return (
    <button
      type="button"
      onMouseEnter={onHover}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 9,
        width: "100%",
        padding: "8px 9px",
        border: "none",
        background: focused ? "color-mix(in srgb, var(--accent) 8%, transparent)" : "transparent",
        boxShadow: focused
          ? "inset 0 0 0 1px color-mix(in srgb, var(--accent) 28%, transparent)"
          : "none",
        borderRadius: 6,
        cursor: "pointer",
        color: focused ? "var(--fg)" : "var(--fg-2)",
        textAlign: "left",
        fontFamily: "Space Grotesk, sans-serif",
      }}
    >
      <span
        style={{
          ...glyphStyle,
          background: `color-mix(in srgb, var(--accent) ${focused || hasSelection ? 14 : 6}%, transparent)`,
          borderColor:
            focused || hasSelection
              ? "color-mix(in srgb, var(--accent) 50%, transparent)"
              : "var(--line-hi)",
          color: focused || hasSelection ? "var(--accent)" : "var(--fg-2)",
        }}
      >
        {p.glyph}
      </span>
      <span style={{ display: "flex", flexDirection: "column", gap: 2, flex: 1, minWidth: 0 }}>
        <span style={{ fontSize: 12.5, fontWeight: 500, color: "var(--fg)" }}>
          {p.name}
          {hasSelection && <ActiveDot />}
        </span>
        <span style={vendorStyle}>{p.vendor}</span>
      </span>
      <span
        style={{
          color: focused ? "var(--accent)" : "var(--fg-3)",
          fontSize: 11,
          opacity: focused ? 1 : 0.35,
        }}
      >
        ›
      </span>
    </button>
  );
}

interface ModelRowProps {
  m: ModelMeta;
  selected: boolean;
  onClick: () => void;
}

export function ModelRow({ m, selected, onClick }: ModelRowProps) {
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 10,
        width: "100%",
        padding: "9px 11px",
        border: "none",
        background: selected ? "color-mix(in srgb, var(--accent) 10%, transparent)" : "transparent",
        boxShadow: selected
          ? "inset 0 0 0 1px color-mix(in srgb, var(--accent) 35%, transparent)"
          : "none",
        borderRadius: 6,
        textAlign: "left",
        cursor: "pointer",
        color: "var(--fg)",
        fontFamily: "Space Grotesk, sans-serif",
      }}
    >
      <span style={{ display: "flex", flexDirection: "column", gap: 3, minWidth: 0, flex: 1 }}>
        <span
          style={{
            fontSize: 12.5,
            fontWeight: 500,
            display: "inline-flex",
            alignItems: "baseline",
            gap: 8,
          }}
        >
          {m.name}
          <Tag selected={selected}>{m.tag}</Tag>
        </span>
        <span style={{ fontSize: 10.5, lineHeight: 1.4, color: "var(--fg-3)" }}>{m.desc}</span>
      </span>
      <span style={metaCol}>
        <span style={{ color: selected ? "var(--accent)" : "var(--fg-2)" }}>{m.ctx}</span>
        <span style={{ color: "var(--fg-3)", opacity: 0.85 }}>{m.cost}</span>
      </span>
    </button>
  );
}

function Tag({ children, selected }: { children: React.ReactNode; selected: boolean }) {
  return (
    <span
      style={{
        fontFamily: "Space Mono, monospace",
        fontSize: 8,
        letterSpacing: "0.14em",
        color: selected ? "var(--accent)" : "var(--fg-3)",
        textTransform: "uppercase",
        padding: "1px 5px",
        border: `1px solid ${selected ? "color-mix(in srgb, var(--accent) 40%, transparent)" : "var(--line-hi)"}`,
        borderRadius: 3,
      }}
    >
      {children}
    </span>
  );
}

function ActiveDot() {
  return (
    <span
      style={{
        width: 5,
        height: 5,
        borderRadius: "50%",
        background: "var(--accent)",
        boxShadow: "0 0 6px var(--glow)",
        marginLeft: 6,
        display: "inline-block",
      }}
    />
  );
}

const glyphStyle = {
  width: 26,
  height: 26,
  borderRadius: 6,
  display: "grid",
  placeItems: "center",
  flexShrink: 0,
  background: "color-mix(in srgb, var(--fg) 6%, transparent)",
  border: "1px solid var(--line-hi)",
  fontFamily: "Space Mono, monospace",
  fontSize: 9.5,
  fontWeight: 700,
  color: "var(--fg-2)",
} as const;

const arrowStyle = {
  fontFamily: "Space Mono, monospace",
  fontSize: 9,
  letterSpacing: "0.1em",
  color: "color-mix(in srgb, var(--accent) 80%, var(--fg-3))",
  whiteSpace: "nowrap",
  padding: "2px 6px",
  border: "1px solid color-mix(in srgb, var(--accent) 30%, transparent)",
  borderRadius: 3,
  background: "color-mix(in srgb, var(--accent) 8%, transparent)",
} as const;

const vendorStyle = {
  fontFamily: "Space Mono, monospace",
  fontSize: 8.5,
  letterSpacing: "0.16em",
  color: "var(--fg-3)",
  textTransform: "uppercase" as const,
};

const metaCol = {
  fontFamily: "Space Mono, monospace",
  fontSize: 9,
  letterSpacing: "0.06em",
  whiteSpace: "nowrap" as const,
  textAlign: "right" as const,
  flexShrink: 0,
  display: "flex",
  flexDirection: "column" as const,
  gap: 2,
  alignItems: "flex-end" as const,
};
