import api from "@/lib/api";

export const portfolioApi = {
  getHoldings: (source?: string) =>
    api.get("/portfolio/holdings", { params: source ? { source } : {} }),
  getTreemap: (source?: string) =>
    api.get("/portfolio/treemap", { params: source ? { source } : {} }),
  getRebalance: () => api.get("/portfolio/rebalance"),
  listSources: () => api.get("/portfolio/sources"),
  getSource: (slug: string) => api.get(`/portfolio/sources/${slug}`),
  syncSource: (slug: string) => api.post(`/portfolio/sources/${slug}/sync`),
  syncAll: () => api.post("/portfolio/sources/sync-all"),
  startLogin: (slug: string) => api.post(`/portfolio/sources/${slug}/start-login`),
  submitOtp: (slug: string, code: string) => api.post(`/portfolio/sources/${slug}/otp`, { code }),
  resetSource: (slug: string) => api.post(`/portfolio/sources/${slug}/reset`),
  listWallets: () => api.get("/portfolio/wallets"),
  syncWallets: () => api.post("/portfolio/wallets/sync"),
  syncWallet: (slug: string) => api.post(`/portfolio/wallets/${slug}/sync`),
};
