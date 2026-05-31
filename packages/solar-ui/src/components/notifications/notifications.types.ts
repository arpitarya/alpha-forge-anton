import type { ReactNode } from "react";

/** Visual variant of a notification — drives icon, color, and pill text.
 * `sync` keys off the active --accent token; the others use locked semantic
 * colors (--ok/--err/--warn/--info/--neutral) so meaning never depends on theme. */
export type Severity = "ok" | "err" | "warn" | "info" | "sync" | "neutral";

export interface NotificationAction {
  label: string;
  /** Visual emphasis — `solid` (primary), `line` (secondary), `ghost` (tertiary). */
  variant?: "solid" | "line" | "ghost";
  onClick: () => void;
}

export interface NotificationInput {
  severity?: Severity;
  title: string;
  /** Short uppercase tag (e.g. "FAILED", "404"). Defaults from severity. */
  pill?: string;
  /** Plain text — HTML is not interpreted, to keep the component XSS-safe. */
  message?: string;
  actions?: NotificationAction[];
  /** Custom icon — overrides the default for the severity. */
  icon?: ReactNode;
  /** ms before auto-dismiss. 0 = persistent. Default: errors and sync persist; others ~5s. */
  ttl?: number;
  /** Render indeterminate progress bar at the bottom — for in-flight operations. */
  indeterminate?: boolean;
  dismissible?: boolean;
  /** Stable key — calling notify with the same id replaces the existing toast. */
  id?: string;
}

export interface Notification extends NotificationInput {
  id: string;
  severity: Severity;
  createdAt: number;
  dismissible: boolean;
}
