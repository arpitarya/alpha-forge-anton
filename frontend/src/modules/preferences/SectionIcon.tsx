import type { ReactNode } from "react";

const PATHS: Record<string, ReactNode> = {
  appearance: <><circle cx="12" cy="12" r="9" /><path d="M12 3a9 9 0 0 0 0 18M3 12h18" /></>,
  display:    <><rect x="3" y="4" width="18" height="13" rx="2" /><path d="M8 21h8M12 17v4" /></>,
  markets:    <><path d="M3 17l5-6 4 4 8-9" /><path d="M16 6h5v5" /></>,
  alpha:      <><rect x="5" y="5" width="14" height="14" rx="2" /><path d="M9 9h6v6H9z" /></>,
  notif:      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10 21a2 2 0 0 0 4 0" />,
  account:    <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  privacy:    <><path d="M12 3l8 4v6c0 5-4 7-8 8-4-1-8-3-8-8V7l8-4z" /><path d="M9 12l2 2 4-4" /></>,
  about:      <><circle cx="12" cy="12" r="9" /><path d="M12 8v4M12 16h.01" /></>,
};

export function SectionIcon({ id }: { id: string }) {
  const path = PATHS[id];
  if (!path) return null;
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth={1.6} aria-hidden>
      {path}
    </svg>
  );
}
