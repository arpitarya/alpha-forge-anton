import api from "@/lib/api";
import type { SizingInputs, SizingResult } from "./flow.sizing.types";

/** POST /flow/sizing — deterministic position sizing (shown, never applied). */
export async function computeSizing(inputs: SizingInputs): Promise<SizingResult> {
  const res = await api.post<SizingResult>("/flow/sizing", inputs);
  return res.data;
}
