import { dismissNotification, pushNotification } from "./notifications.store";
import type { NotificationInput } from "./notifications.types";

type Shortcut = Omit<NotificationInput, "severity" | "title"> & { title: string };

/** Imperative notification API — usable from anywhere (event handlers, effects,
 * non-React code). Each call returns the toast id so callers can update or
 * dismiss it later. */
export const notify = {
  ok: (input: Shortcut) => pushNotification({ ...input, severity: "ok" }),
  error: (input: Shortcut) => pushNotification({ ...input, severity: "err" }),
  warn: (input: Shortcut) => pushNotification({ ...input, severity: "warn" }),
  info: (input: Shortcut) => pushNotification({ ...input, severity: "info" }),
  sync: (input: Shortcut) =>
    pushNotification({ ...input, severity: "sync", indeterminate: input.indeterminate ?? true }),
  /** Full control — pass a complete NotificationInput, including a custom severity. */
  custom: (input: NotificationInput) => pushNotification(input),
  /** Update an existing toast by re-pushing with the same id (or push a new one). */
  upsert: (input: NotificationInput & { id: string }) => pushNotification(input),
  dismiss: (id: string) => dismissNotification(id),
};
