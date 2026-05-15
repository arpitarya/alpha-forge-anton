import api from "@/lib/api";
import type { BootReport } from "./boot.types";

/** Snapshot of every backend system the boot splash cares about. Single
 * round-trip — backend already aggregates DB + every broker source. */
export async function fetchBootReport(): Promise<BootReport> {
  const res = await api.get<BootReport>("/health/boot");
  return res.data;
}
