"use client";

import { usePlan, usePlanDrift, useProjection } from "../plans/plans.query";
import { useHoldings, useTreemap } from "../portfolio/portfolio.query";
import type { UINode } from "./compose.types";
import { DynamicRenderer } from "./DynamicRenderer";

interface Props {
  spec: UINode;
}

/**
 * Resolves the composable data hooks (backend COMPOSABLE_HOOKS) and feeds the
 * results to DynamicRenderer. Every hook is called unconditionally — Rules of
 * Hooks stay intact and react-query dedupes against the dashboard's own queries,
 * so unused bindings cost a cache lookup, not a request storm.
 */
export function SpecHost({ spec }: Props) {
  const holdings = useHoldings();
  const treemap = useTreemap();
  const plan = usePlan();
  const drift = usePlanDrift();
  const projection = useProjection();

  const data: Record<string, Record<string, unknown>> = {
    useHoldings: (holdings.data ?? {}) as Record<string, unknown>,
    useTreemap: (treemap.data ?? {}) as Record<string, unknown>,
    usePlan: (plan.data ?? {}) as Record<string, unknown>,
    usePlanDrift: (drift.data ?? {}) as Record<string, unknown>,
    useProjection: (projection.data ?? {}) as Record<string, unknown>,
  };

  return <DynamicRenderer node={spec} data={data} />;
}
