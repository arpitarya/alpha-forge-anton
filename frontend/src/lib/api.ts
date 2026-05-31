import axios from "axios";

import { type ApiError, toApiError } from "@/lib/apiError";
import { getLogger } from "@/lib/logger";

const log = getLogger("api");

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Opt-out flag for requests that must NOT trigger the 401 refresh dance —
// notably the refresh endpoint itself (otherwise a 401 from /iam/refresh
// would re-call silentRefresh → infinite loop) and the login endpoints.
declare module "axios" {
  export interface AxiosRequestConfig {
    skipAuthRefresh?: boolean;
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.skipAuthRefresh &&
      typeof window !== "undefined" &&
      window.location.pathname !== "/login"
    ) {
      original._retry = true;
      try {
        const { useAuthStore } = await import("@/modules/auth/useAuthStore");
        await useAuthStore.getState().silentRefresh();
        const token = localStorage.getItem("af_token");
        if (token) original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      } catch {
        const { useAuthStore } = await import("@/modules/auth/useAuthStore");
        useAuthStore.getState().clearAuth();
        window.location.replace("/login");
      }
    }
    const apiErr: ApiError = toApiError(error);
    // Canceled requests are not failures — they happen on unmount, debounce, etc.
    // Logging them as errors creates noise and triggers false-positive alerting.
    if (apiErr.kind !== "canceled") {
      log.error(
        { status: apiErr.status, url: apiErr.url, kind: apiErr.kind, requestId: apiErr.requestId },
        "API request failed: %s",
        apiErr.message,
      );
    }
    // Attach the normalized error so consumers can read it without re-parsing axios shape.
    (error as { apiError?: ApiError }).apiError = apiErr;
    return Promise.reject(error);
  },
);

export default api;
export { type ApiError, toApiError } from "@/lib/apiError";
