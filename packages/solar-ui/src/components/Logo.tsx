import type { HTMLAttributes } from "react";

// Anton mark: ascending bars breaking out — market making a new high
// Palette: #FFB454 → #F38A2B → #D45A1A, accent: #ff8f00

type LogoVariant = "icon" | "lockup";
type LogoSize = "xs" | "sm" | "md" | "lg" | "xl";

export interface LogoProps extends HTMLAttributes<HTMLElement> {
  variant?: LogoVariant;
  size?: LogoSize;
}

const ICON_PX: Record<LogoSize, number> = { xs: 20, sm: 28, md: 36, lg: 48, xl: 64 };

function AntonMark({ size, gradId }: { size: number; gradId: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden focusable="false">
      <title>Anton</title>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#FFB454" />
          <stop offset="55%" stopColor="#F38A2B" />
          <stop offset="100%" stopColor="#D45A1A" />
        </linearGradient>
      </defs>
      <rect x="9" y="52.5" width="46" height="2.6" rx="1.3" fill="#000" opacity=".22" />
      <rect x="11" y="40" width="9" height="12.5" rx="1.6" fill={`url(#${gradId})`} />
      <rect x="27.5" y="30" width="9" height="22.5" rx="1.6" fill={`url(#${gradId})`} />
      <rect x="44" y="21" width="9" height="31.5" rx="1.6" fill={`url(#${gradId})`} />
      <path d="M41.5 22 L55.5 22 L48.5 9 Z" fill={`url(#${gradId})`} />
      <rect x="44" y="21" width="2.6" height="31.5" rx="1.3" fill="#fff" opacity=".2" />
      <rect x="27.5" y="30" width="2.4" height="22.5" rx="1.2" fill="#fff" opacity=".14" />
    </svg>
  );
}

export function Logo({ variant = "icon", size = "md", style, ...props }: LogoProps) {
  const px = ICON_PX[size];
  const glow = { filter: "drop-shadow(0 0 14px #ff8f0038)" };

  if (variant === "icon") {
    return (
      <span
        style={{ display: "block", ...glow, ...style }}
        role="img"
        aria-label="Anton"
        {...(props as HTMLAttributes<HTMLSpanElement>)}
      >
        <AntonMark size={px} gradId="af-icon-g" />
      </span>
    );
  }

  // lockup: icon | vertical rule | ALPHA FORGE / ANTON / TRADING TERMINAL
  const rule = Math.round(px * 1.4);
  const eyePx = Math.max(6, Math.round(px * 0.36));
  const namePx = Math.max(10, Math.round(px * 0.58));
  const rolePx = Math.max(6, Math.round(px * 0.32));
  const gap = Math.round(px * 0.65);

  return (
    <div
      style={{ display: "flex", alignItems: "center", gap, ...style }}
      role="img"
      aria-label="Anton — Trading Terminal"
      {...(props as HTMLAttributes<HTMLDivElement>)}
    >
      <span style={glow}>
        <AntonMark size={px} gradId="af-lock-g" />
      </span>
      <div
        aria-hidden
        style={{
          width: 1,
          height: rule,
          background: "linear-gradient(180deg,transparent,rgba(255,255,255,.14),transparent)",
          flexShrink: 0,
        }}
      />
      <div aria-hidden style={{ display: "flex", flexDirection: "column", lineHeight: 1 }}>
        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: eyePx, letterSpacing: "0.34em", color: "var(--fg-3)", marginBottom: Math.round(eyePx * 0.55) }}>
          ALPHA FORGE
        </span>
        <span style={{ fontWeight: 700, fontSize: namePx, letterSpacing: "0.16em", color: "var(--fg)" }}>
          ANTON
        </span>
        <span style={{ fontFamily: "'Space Mono',monospace", fontSize: rolePx, letterSpacing: "0.26em", color: "#ff8f00", marginTop: Math.round(rolePx * 0.55) }}>
          TRADING TERMINAL
        </span>
      </div>
    </div>
  );
}
