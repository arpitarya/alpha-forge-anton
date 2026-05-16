import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { dashboardApi } from "./dashboard.api";
import type {
  DashboardStatsDTO,
  RiskMeterDTO,
  TerminalBriefDTO,
  TickerItemDTO,
  WatchlistItemDTO,
} from "./dashboard.types";

export function useDashboardTicker() {
  return useQuery<TickerItemDTO[]>({
    queryKey: ["dashboard", "ticker"],
    queryFn: () => dashboardApi.getTicker().then((r) => r.data),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

export function useDashboardWatchlist() {
  return useQuery<WatchlistItemDTO[]>({
    queryKey: ["dashboard", "watchlist"],
    queryFn: () => dashboardApi.getWatchlist().then((r) => r.data),
    staleTime: 5_000,
    refetchInterval: 5_000,
  });
}

export function useDashboardRisk() {
  return useQuery<RiskMeterDTO>({
    queryKey: ["dashboard", "risk"],
    queryFn: () => dashboardApi.getRisk().then((r) => r.data),
    staleTime: 4_000,
    refetchInterval: 4_000,
  });
}

export function useDashboardBrief() {
  return useQuery<TerminalBriefDTO>({
    queryKey: ["dashboard", "brief"],
    queryFn: () => dashboardApi.getBrief().then((r) => r.data),
    staleTime: 60_000,
  });
}

export function useAddTickerItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (symbol: string) => dashboardApi.addTicker(symbol).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboard", "ticker"] }),
  });
}

export function useDeleteTickerItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => dashboardApi.deleteTicker(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboard", "ticker"] }),
  });
}

export function useAddWatchlistItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { symbol: string; sublabel: string }) =>
      dashboardApi.addWatchlist(params.symbol, params.sublabel).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboard", "watchlist"] }),
  });
}

export function useDeleteWatchlistItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => dashboardApi.deleteWatchlist(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboard", "watchlist"] }),
  });
}

export function useDashboardStats() {
  return useQuery<DashboardStatsDTO>({
    queryKey: ["dashboard", "stats"],
    queryFn: () => dashboardApi.getStats().then((r) => r.data),
    staleTime: 5_000,
    refetchInterval: 5_000,
  });
}
