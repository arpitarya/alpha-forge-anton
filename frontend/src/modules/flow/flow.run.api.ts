import api from "@/lib/api";
import type { RunStatus } from "./flow.run.types";

/** POST /flow/edges/{id}/run — start (or rejoin) the async funnel run for an edge. */
export async function startRun(edgeId: string): Promise<RunStatus> {
  const res = await api.post<RunStatus>(`/flow/edges/${encodeURIComponent(edgeId)}/run`);
  return res.data;
}

/** GET /flow/runs/{job_id} — poll one run's live status. */
export async function fetchRun(jobId: string): Promise<RunStatus> {
  const res = await api.get<RunStatus>(`/flow/runs/${encodeURIComponent(jobId)}`);
  return res.data;
}

/** GET /flow/edges/{id}/run — the latest in-session run for an edge (null if none). */
export async function fetchLatestRun(edgeId: string): Promise<RunStatus | null> {
  const res = await api.get<RunStatus | null>(`/flow/edges/${encodeURIComponent(edgeId)}/run`);
  return res.data;
}
