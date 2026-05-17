import api from "@/lib/api";
import type { BootReport, BootSyncReport } from "./boot.types";

/** Snapshot of every backend system the boot splash cares about. Single
 * round-trip — backend already aggregates DB + every broker source. */
export async function fetchBootReport(): Promise<BootReport> {
  const res = await api.get<BootReport>("/health/boot");
  return res.data;
}

/** Trigger concurrent sync of all linked broker sources. Call immediately
 * after fetchBootReport; resolves when all syncs settle. */
export async function triggerBootSync(): Promise<BootSyncReport> {
  const res = await api.post<BootSyncReport>("/health/boot/sync");
  return res.data;
}
