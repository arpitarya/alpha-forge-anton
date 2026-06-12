import {
  AllocationBar,
  Badge,
  Card,
  Chip,
  CountUp,
  DataTable,
  DeltaText,
  Divider,
  DonutChart,
  Icon,
  Kbd,
  LineChart,
  LiveDot,
  ProgressBar,
  RiskBars,
  Sparkline,
  Stat,
  StatGrid,
  Text,
} from "@alphaforge-anton/solar-ui";
import type { ComponentType } from "react";

/**
 * The client-side whitelist — the ONLY components a generated UISpec may mount.
 * This is the second line of defence: even if the backend validator were bypassed,
 * nothing outside this map can ever render. No `eval`, no dynamic imports.
 * Must mirror backend COMPOSABLE_COMPONENTS (compose_registry.py) — guarded by
 * `just probe compose-registry`.
 */
// biome-ignore lint/suspicious/noExplicitAny: props are validated upstream by Fux
export const WHITELIST: Record<string, ComponentType<any>> = {
  AllocationBar,
  Badge,
  Card,
  Chip,
  CountUp,
  DataTable,
  DeltaText,
  Divider,
  DonutChart,
  Icon,
  Kbd,
  LineChart,
  LiveDot,
  ProgressBar,
  RiskBars,
  Sparkline,
  Stat,
  StatGrid,
  Text,
};
