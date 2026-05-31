import axios, { type AxiosError } from "axios";

export type ApiErrorKind =
  | "network" // request never reached the server (offline, DNS, connection refused)
  | "canceled" // AbortController aborted the request — not a real failure
  | "auth" // 401 — token missing/expired (interceptor handles refresh)
  | "forbidden" // 403
  | "notFound" // 404
  | "validation" // 422
  | "client" // other 4xx
  | "server" // 5xx
  | "unknown";

export interface ApiError {
  kind: ApiErrorKind;
  status: number; // 0 for network/canceled
  message: string; // human-readable, derived from FastAPI {detail} when present
  detail?: unknown; // raw FastAPI payload for callers that need structure
  requestId?: string; // x-request-id from response, when backend provides it
  url?: string;
  method?: string;
  /** Original axios error for callers that really need it (rare). */
  cause?: AxiosError;
}

function kindFromStatus(status: number): ApiErrorKind {
  if (status === 401) return "auth";
  if (status === 403) return "forbidden";
  if (status === 404) return "notFound";
  if (status === 422) return "validation";
  if (status >= 500) return "server";
  if (status >= 400) return "client";
  return "unknown";
}

// FastAPI typically returns {detail: "msg"} or {detail: [{loc, msg, type}, ...]}.
// Pull a single readable string out of either shape.
function extractDetail(data: unknown): string | undefined {
  if (!data || typeof data !== "object") return undefined;
  const d = (data as { detail?: unknown }).detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d) && d.length > 0) {
    const first = d[0] as { msg?: unknown; loc?: unknown };
    if (typeof first.msg === "string") {
      const loc = Array.isArray(first.loc) ? first.loc.join(".") : "";
      return loc ? `${first.msg} (${loc})` : first.msg;
    }
  }
  return undefined;
}

const FRIENDLY: Record<ApiErrorKind, string> = {
  network: "Can't reach the server. Check your connection.",
  canceled: "Request canceled.",
  auth: "Your session expired. Please sign in again.",
  forbidden: "You don't have access to this.",
  notFound: "Not found.",
  validation: "Some inputs were invalid.",
  client: "Request couldn't be completed.",
  server: "Server hit an error. Try again in a moment.",
  unknown: "Something went wrong.",
};

export function toApiError(err: unknown): ApiError {
  if (axios.isCancel(err)) {
    return { kind: "canceled", status: 0, message: FRIENDLY.canceled };
  }
  if (axios.isAxiosError(err)) {
    const ax = err as AxiosError;
    const status = ax.response?.status ?? 0;
    if (status === 0) {
      return {
        kind: "network",
        status: 0,
        message: FRIENDLY.network,
        url: ax.config?.url,
        method: ax.config?.method?.toUpperCase(),
        cause: ax,
      };
    }
    const kind = kindFromStatus(status);
    const detailMsg = extractDetail(ax.response?.data);
    return {
      kind,
      status,
      message: detailMsg ?? FRIENDLY[kind],
      detail: ax.response?.data,
      requestId: (ax.response?.headers?.["x-request-id"] as string | undefined) ?? undefined,
      url: ax.config?.url,
      method: ax.config?.method?.toUpperCase(),
      cause: ax,
    };
  }
  return {
    kind: "unknown",
    status: 0,
    message: err instanceof Error ? err.message : FRIENDLY.unknown,
  };
}

export function isApiError(x: unknown): x is ApiError {
  return !!x && typeof x === "object" && "kind" in x && "status" in x && "message" in x;
}
