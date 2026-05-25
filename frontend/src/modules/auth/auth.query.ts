import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { extendSession, listSessions, revokeSession } from "./auth.api"
import type { SessionResponse } from "./auth.types"

export function useSessions() {
  return useQuery<SessionResponse[]>({
    queryKey: ["iam", "sessions"],
    queryFn: listSessions,
  })
}

export function useExtendSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, extra_minutes }: { id: string; extra_minutes?: number | null }) =>
      extendSession(id, extra_minutes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["iam", "sessions"] }),
  })
}

export function useRevokeSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => revokeSession(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["iam", "sessions"] }),
  })
}
