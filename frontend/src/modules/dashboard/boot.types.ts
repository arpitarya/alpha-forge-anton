/** Mirrors `BootService` in `backend/app/modules/health/boot_schemas.py`. */
export type BootStatus = "ok" | "warn" | "error" | "skip";

export interface BootService {
  key: string;
  label: string;
  status: BootStatus;
  detail: string;
}

export interface BootReport {
  services: BootService[];
}

/** Mirrors per-event payload from GET /health/boot/sync-stream. */
export interface SyncResult {
  ok: boolean;
  holdings_count: number;
  detail: string;
  /** Raw failure reason from the backend (exception message, timeout, vault-lock).
   * Present when ok=false, or when the source is unconfigured for a recoverable
   * reason (e.g. vault locked). The frontend uses this to propose a fix. */
  reason?: string;
}
