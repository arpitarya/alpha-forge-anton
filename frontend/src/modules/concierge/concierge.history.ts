import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface SessionMeta {
  id: string;
  title: string;
}

export interface SessionTurnDTO {
  query: string;
  response: string;
  provider: string | null;
  model: string | null;
}

export interface SessionDoc extends SessionMeta {
  turns: SessionTurnDTO[];
}

export interface SaveSessionInput extends SessionMeta {
  turns: SessionTurnDTO[];
}

const KEY = ["concierge", "history"];

/** Past conversations for the history sidebar (elgar-backed, see history_service.py). */
export function useHistory() {
  return useQuery<SessionMeta[]>({
    queryKey: KEY,
    queryFn: () => api.get("/concierge/history").then((r) => r.data),
    staleTime: 30_000,
  });
}

/** Load one stored conversation's turns — called on demand to resume it. */
export function loadSession(id: string): Promise<SessionDoc> {
  return api.get(`/concierge/history/${id}`).then((r) => r.data);
}

/** Persist (overwrite) the active conversation; refreshes the sidebar quietly. */
export function useSaveSession() {
  const qc = useQueryClient();
  return useMutation<SessionMeta, Error, SaveSessionInput>({
    mutationFn: ({ id, title, turns }) =>
      api.put(`/concierge/history/${id}`, { title, turns }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => api.delete(`/concierge/history/${id}`).then(() => undefined),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}
