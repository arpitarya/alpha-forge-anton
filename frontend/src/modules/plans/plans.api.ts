import api from "@/lib/api";

export const plansApi = {
  getPlan: (planId?: string) =>
    api.get("/plans", { params: planId ? { plan_id: planId } : {} }),
  getDrift: (planId?: string) =>
    api.get("/plans/drift", { params: planId ? { plan_id: planId } : {} }),
  getProjection: (params?: {
    years?: number;
    monthly?: number;
    initial?: number;
    asset_class?: string;
  }) => api.get("/plans/projection", { params: params ?? {} }),
  /** Save a plan document into the private elgar store — see `fux why plan-store`. */
  savePlan: (title: string, content: string) => api.post("/plans", { title, content }),
};
