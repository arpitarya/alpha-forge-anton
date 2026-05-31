import { notify } from "@alphaforge-anton/solar-ui";
import type { ApiError } from "@/lib/apiError";

const TITLES: Record<ApiError["kind"], string> = {
  network: "You're offline",
  canceled: "",
  auth: "",
  forbidden: "Access denied",
  notFound: "Not found",
  validation: "Invalid input",
  client: "Request failed",
  server: "Server error",
  unknown: "Something went wrong",
};

/** Bridge: turn a normalized ApiError into a toast. Skips `canceled` (noise)
 * and `auth` (the axios interceptor already redirects to /login). */
export function notifyApiError(err: ApiError, fallbackTitle = "Request failed"): string | null {
  if (err.kind === "canceled" || err.kind === "auth") return null;
  return notify.error({
    title: TITLES[err.kind] || fallbackTitle,
    pill: err.status ? `${err.status}` : err.kind.toUpperCase(),
    message: err.message,
  });
}
