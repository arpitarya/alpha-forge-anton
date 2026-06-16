import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export interface ObjectiveStepUp {
  from_date: string;
  monthly_target_inr: number;
}

/** The north-star Orff optimises toward. Read-only here — edits route through the
 * `set_objective` tool → ApprovalCard → elgar commit, never a silent write. */
export interface Objective {
  monthly_target_inr: number;
  step_up: ObjectiveStepUp | null;
  horizon: "swing" | "long_term";
  risk_tolerance: "conservative" | "moderate" | "aggressive";
  mission: string;
  /** `step_up` resolved by today's date — the figure the bar measures against. */
  active_target: number;
}

/** GET /signals/objective — typed objective + active_target. Deliberately carries
 * NO progress: there is no trades source yet, so MTD renders as a pending state. */
export function useObjective() {
  return useQuery<Objective>({
    queryKey: ["signals", "objective"],
    queryFn: () => api.get("/signals/objective").then((r) => r.data),
    staleTime: 60_000,
  });
}
