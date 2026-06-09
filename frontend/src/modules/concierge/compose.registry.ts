import {
  Badge,
  Card,
  Chip,
  CountUp,
  Divider,
  Icon,
  Kbd,
  LiveDot,
  ProgressBar,
  RiskBars,
  Sparkline,
  Stat,
} from "@alphaforge-anton/solar-ui";
import type { ComponentType } from "react";

/**
 * The client-side whitelist — the ONLY components a generated UISpec may mount.
 * This is the second line of defence: even if the backend validator were bypassed,
 * nothing outside this map can ever render. No `eval`, no dynamic imports.
 */
// biome-ignore lint/suspicious/noExplicitAny: props are validated upstream by Fux
export const WHITELIST: Record<string, ComponentType<any>> = {
  Badge,
  Card,
  Chip,
  CountUp,
  Divider,
  Icon,
  Kbd,
  LiveDot,
  ProgressBar,
  RiskBars,
  Sparkline,
  Stat,
};
