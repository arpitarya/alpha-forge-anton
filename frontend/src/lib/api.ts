import axios from "axios";

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

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
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
    log.error(
      { status: error.response?.status, url: error.config?.url },
      "API request failed: %s",
      error.message,
    );
    return Promise.reject(error);
  },
);

export default api;
