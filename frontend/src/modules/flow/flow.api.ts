import api from "@/lib/api";
import type {
  AuthorEdgeRequest,
  EdgeListItem,
  EdgeTemplate,
  FlowState,
  StageStatus,
} from "./flow.types";

/** GET /flow/stages — the locked 9-node flow skeleton (labels + order). */
export async function fetchStages(): Promise<StageStatus[]> {
  const res = await api.get<StageStatus[]>("/flow/stages");
  return res.data;
}

/** GET /flow/templates — Idea-stage candidates (Family A/B real; C scaffolded). */
export async function fetchTemplates(): Promise<EdgeTemplate[]> {
  const res = await api.get<EdgeTemplate[]>("/flow/templates");
  return res.data;
}

/** GET /flow/edges — every cockpit edge with its furthest stage. */
export async function fetchEdges(): Promise<EdgeListItem[]> {
  const res = await api.get<EdgeListItem[]>("/flow/edges");
  return res.data;
}

/** GET /flow/edges/{id} — one edge's 9-stage cockpit state. */
export async function fetchFlowState(edgeId: string): Promise<FlowState> {
  const res = await api.get<FlowState>(`/flow/edges/${encodeURIComponent(edgeId)}`);
  return res.data;
}

/** POST /flow/edges — author + pre-register a new edge (server-stamps the timestamp). */
export async function authorEdge(req: AuthorEdgeRequest): Promise<FlowState> {
  const res = await api.post<FlowState>("/flow/edges", req);
  return res.data;
}
