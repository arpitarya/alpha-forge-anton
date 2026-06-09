import api from "@/lib/api";

import type { ComposeResponse } from "./compose.types";

/** Ask Orff to compose a UI; the backend returns a Fux-validated UISpec (§18.3). */
export async function composeUI(prompt: string, provider = "auto"): Promise<ComposeResponse> {
  const { data } = await api.post<ComposeResponse>("/concierge/compose", { prompt, provider });
  return data;
}
