import api from "@/lib/api";
import type { Objective } from "@/modules/contracts";

/** One discovery run in the edge-library funnel (counts only — no ₹, no holdings). */
export interface RecentRun {
  edge_id: string;
  run_at: string;
  verdict: "PASS" | "KILL";
  gate_reached: number;
}

/** GET /edges/summary — the journal aggregated to the edge-library band. */
export interface EdgeSummary {
  tested: number;
  killed: number;
  passed: number;
  live: number;
  kill_rate: number; // 0.0–1.0
  recent: RecentRun[];
}

/** The program mandate — the elgar-stored Objective, loaded at runtime (never committed). */
export async function fetchMandate(): Promise<Objective> {
  const res = await api.get<Objective>("/mandate");
  return res.data;
}

/** The edge-library funnel from the discovery journal. */
export async function fetchEdgeSummary(): Promise<EdgeSummary> {
  const res = await api.get<EdgeSummary>("/edges/summary");
  return res.data;
}
