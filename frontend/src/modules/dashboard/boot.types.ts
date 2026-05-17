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

/** Mirrors `POST /health/boot/sync` response. */
export interface SyncResult {
  ok: boolean;
  holdings_count: number;
  detail: string;
}

export interface BootSyncReport {
  results: Record<string, SyncResult>;
}
