import api from "@/lib/api";

export const dashboardApi = {
  getTicker: () => api.get("/dashboard/ticker"),
  addTicker: (symbol: string) => api.post("/dashboard/ticker", { symbol }),
  deleteTicker: (id: string) => api.delete(`/dashboard/ticker/${id}`),
  getWatchlist: () => api.get("/dashboard/watchlist"),
  addWatchlist: (symbol: string, sublabel: string) =>
    api.post("/dashboard/watchlist", { symbol, sublabel }),
  deleteWatchlist: (id: string) => api.delete(`/dashboard/watchlist/${id}`),
  getRisk: () => api.get("/dashboard/risk"),
  getBrief: () => api.get("/dashboard/brief"),
  getStats: () => api.get("/dashboard/stats"),
};
