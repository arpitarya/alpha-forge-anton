"use client";

import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode, useState } from "react";

import { type ApiError, toApiError } from "@/lib/apiError";
import { notifyApiError } from "@/lib/apiNotify";

// Don't retry user-facing errors — only network blips and 5xx make sense to retry.
function shouldRetry(failureCount: number, error: unknown): boolean {
  if (failureCount >= 2) return false;
  const apiErr: ApiError = toApiError(error);
  if (apiErr.kind === "canceled" || apiErr.kind === "auth") return false;
  return apiErr.kind === "network" || apiErr.kind === "server";
}

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 1000,
            refetchOnWindowFocus: true,
            retry: shouldRetry,
            retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10_000),
          },
          mutations: { retry: false },
        },
        // Mutations are user-initiated — surface failures by default.
        // Queries are noisier (background refetches, polling); components opt in
        // via useQuery({ meta: { notifyOnError: true } }).
        mutationCache: new MutationCache({
          onError: (err, _vars, _ctx, mutation) => {
            if (mutation.meta?.silent === true) return;
            const apiErr = toApiError(err);
            if (apiErr.kind === "canceled" || apiErr.kind === "auth") return;
            notifyApiError(apiErr);
          },
        }),
        queryCache: new QueryCache({
          onError: (err, query) => {
            if (query.meta?.notifyOnError !== true) return;
            const apiErr = toApiError(err);
            if (apiErr.kind === "canceled" || apiErr.kind === "auth") return;
            notifyApiError(apiErr);
          },
        }),
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

declare module "@tanstack/react-query" {
  interface Register {
    queryMeta: { notifyOnError?: boolean };
    mutationMeta: { silent?: boolean };
  }
}
