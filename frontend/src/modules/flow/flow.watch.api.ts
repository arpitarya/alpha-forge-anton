import api from "@/lib/api";
import type { Observation, RetirementRecord, WatchState } from "./flow.watch.types";

/** POST /flow/edges/{id}/watch — deterministic decay read-back from the realized series. */
export async function fetchWatch(edgeId: string, observations: Observation[]): Promise<WatchState> {
  const res = await api.post<WatchState>(`/flow/edges/${encodeURIComponent(edgeId)}/watch`, {
    observations,
  });
  return res.data;
}

/** POST /flow/edges/{id}/decay-kill — retire a decayed edge (journals to elgar). */
export async function decayKill(
  edgeId: string,
  observations: Observation[],
  reason: string,
): Promise<RetirementRecord> {
  const res = await api.post<RetirementRecord>(
    `/flow/edges/${encodeURIComponent(edgeId)}/decay-kill`,
    { observations, reason },
  );
  return res.data;
}
