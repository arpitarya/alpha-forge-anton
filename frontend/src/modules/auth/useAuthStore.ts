import { create } from "zustand";
import { persist } from "zustand/middleware";

import { getLogger } from "@/lib/logger";

import { api, getMe, logoutUser, refreshTokens } from "./auth.api";
import type { IamUser, TokenResponse } from "./auth.types";

const ACCESS_KEY = "af_token";
const REFRESH_KEY = "af_refresh_token";
const log = getLogger("auth");

interface AuthState {
  user: IamUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (tokens: TokenResponse) => void;
  setUser: (user: IamUser) => void;
  clearAuth: () => void;
  logout: () => Promise<void>;
  silentRefresh: () => Promise<void>;
  bootstrap: () => Promise<void>;
}

function applyHeader(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    localStorage.setItem(ACCESS_KEY, token);
  } else {
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem(ACCESS_KEY);
  }
}

function requestPath(url: unknown): string {
  return typeof url === "string" ? url.split("?")[0] : "";
}

function skipRefreshRetry(url: unknown): boolean {
  return new Set([
    "/iam/login",
    "/iam/logout",
    "/iam/refresh",
    "/iam/register",
    "/iam/login-key",
  ]).has(requestPath(url));
}

function errorStatus(err: unknown): number | undefined {
  if (!err || typeof err !== "object") return undefined;
  const response = (err as { response?: { status?: number } }).response;
  return response?.status;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : "unknown error";
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setTokens: (t) => {
        applyHeader(t.access_token);
        localStorage.setItem(REFRESH_KEY, t.refresh_token);
        set({ accessToken: t.access_token, refreshToken: t.refresh_token });
      },
      setUser: (user) => set({ user }),
      clearAuth: () => {
        applyHeader(null);
        localStorage.removeItem(REFRESH_KEY);
        set({ user: null, accessToken: null, refreshToken: null });
      },
      logout: async () => {
        const { refreshToken: rt } = get();
        if (rt) {
          try {
            await logoutUser(rt);
          } catch (err) {
            log.warn(
              { status: errorStatus(err) },
              "Logout token revocation failed; clearing local session anyway: %s",
              errorMessage(err),
            );
          }
        }
        get().clearAuth();
      },
      silentRefresh: async () => {
        const rt = get().refreshToken;
        if (!rt) throw new Error("no refresh token");
        const tokens = await refreshTokens(rt);
        get().setTokens(tokens);
      },
      bootstrap: async () => {
        const at = get().accessToken;
        if (!at) return;
        applyHeader(at);
        try {
          const me = await getMe();
          set({ user: me });
        } catch {
          try {
            await get().silentRefresh();
            set({ user: await getMe() });
          } catch {
            get().clearAuth();
          }
        }
      },
    }),
    { name: "af-auth" },
  ),
);

let refreshing: Promise<void> | null = null;
api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const original = err.config;
    if (
      err.response?.status === 401 &&
      original &&
      !original._retry &&
      !skipRefreshRetry(original.url)
    ) {
      original._retry = true;
      refreshing = refreshing ?? useAuthStore.getState().silentRefresh();
      try {
        await refreshing;
      } finally {
        refreshing = null;
      }
      original.headers.Authorization = api.defaults.headers.common.Authorization;
      return api(original);
    }
    return Promise.reject(err);
  },
);
