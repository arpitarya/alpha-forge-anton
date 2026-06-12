import { useMutation, useQuery } from "@tanstack/react-query";
import { plansApi } from "./plans.api";
import type { PlanDriftDTO, PlanDTO, PlanSaveResponseDTO, ProjectionDTO } from "./plans.types";

export function usePlan(planId?: string) {
  return useQuery<PlanDTO>({
    queryKey: ["plans", "plan", planId ?? "core-allocation"],
    queryFn: () => plansApi.getPlan(planId).then((r) => r.data),
    staleTime: 60_000,
  });
}

export function usePlanDrift(planId?: string) {
  return useQuery<PlanDriftDTO>({
    queryKey: ["plans", "drift", planId ?? "core-allocation"],
    queryFn: () => plansApi.getDrift(planId).then((r) => r.data),
    staleTime: 30_000,
  });
}

/** Default projection: live portfolio value forward 10y at the plan-mix rate. */
export function useProjection() {
  return useQuery<ProjectionDTO>({
    queryKey: ["plans", "projection", "default"],
    queryFn: () => plansApi.getProjection().then((r) => r.data),
    staleTime: 60_000,
  });
}

export function useSavePlan() {
  return useMutation<PlanSaveResponseDTO, Error, { title: string; content: string }>({
    mutationFn: ({ title, content }) =>
      plansApi.savePlan(title, content).then((r) => r.data),
  });
}
