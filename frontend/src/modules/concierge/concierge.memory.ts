import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface MemoryDoc {
  content: string;
}

const KEY = ["concierge", "memory"];

/** The user-editable context Orff injects into every chat (server-stored). */
export function useConciergeMemory() {
  return useQuery<MemoryDoc>({
    queryKey: KEY,
    queryFn: () => api.get("/concierge/memory").then((r) => r.data),
    staleTime: 60_000,
  });
}

export function useSaveMemory() {
  const qc = useQueryClient();
  return useMutation<MemoryDoc, Error, string>({
    mutationFn: (content) => api.put("/concierge/memory", { content }).then((r) => r.data),
    onSuccess: (doc) => qc.setQueryData(KEY, doc),
  });
}
