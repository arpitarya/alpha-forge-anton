import type { ReactNode } from "react";
import type { Severity } from "./notifications.types";

const stroke = { fill: "none", stroke: "currentColor", strokeWidth: 2 } as const;

const Ok = (
  <svg viewBox="0 0 24 24" {...stroke} strokeWidth={2.2} aria-hidden="true">
    <title>Success</title>
    <path d="M20 6 9 17l-5-5" />
  </svg>
);
const Err = (
  <svg viewBox="0 0 24 24" {...stroke} strokeWidth={2.2} aria-hidden="true">
    <title>Error</title>
    <path d="M18 6 6 18M6 6l12 12" />
  </svg>
);
const Warn = (
  <svg viewBox="0 0 24 24" {...stroke} aria-hidden="true">
    <title>Warning</title>
    <path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
  </svg>
);
const Info = (
  <svg viewBox="0 0 24 24" {...stroke} aria-hidden="true">
    <title>Info</title>
    <circle cx="12" cy="12" r="10" />
    <path d="M12 16v-4M12 8h.01" />
  </svg>
);
const Sync = (
  <svg viewBox="0 0 24 24" {...stroke} className="af-spin" aria-hidden="true">
    <title>Syncing</title>
    <path d="M21 12a9 9 0 1 1-2.64-6.36" />
    <path d="M21 3v6h-6" />
  </svg>
);

const MAP: Record<Severity, ReactNode> = {
  ok: Ok,
  err: Err,
  warn: Warn,
  info: Info,
  sync: Sync,
  neutral: Info,
};

export function severityIcon(sev: Severity): ReactNode {
  return MAP[sev];
}

export const CloseIcon = (
  <svg viewBox="0 0 24 24" {...stroke} aria-hidden="true">
    <title>Dismiss</title>
    <path d="M18 6 6 18M6 6l12 12" />
  </svg>
);
