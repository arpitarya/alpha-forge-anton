import api from "@/lib/api";
import type { RedteamReport } from "./flow.redteam.types";

/** POST /flow/edges/{id}/redteam — start the cage-metered LLM critique for a surviving edge. */
export async function startRedteam(edgeId: string): Promise<RedteamReport> {
  const res = await api.post<RedteamReport>(`/flow/edges/${encodeURIComponent(edgeId)}/redteam`);
  return res.data;
}

/** GET /flow/edges/{id}/redteam — poll the latest red-team report (null until run). */
export async function fetchRedteam(edgeId: string): Promise<RedteamReport | null> {
  const res = await api.get<RedteamReport | null>(
    `/flow/edges/${encodeURIComponent(edgeId)}/redteam`,
  );
  return res.data;
}
