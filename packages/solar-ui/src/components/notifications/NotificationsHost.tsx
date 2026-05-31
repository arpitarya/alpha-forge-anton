"use client";

import { Notification } from "./Notification";
import { useNotifications } from "./notifications.store";

export interface NotificationsHostProps {
  /** Visual placement of the toast stack. Default: `bottom-right`. */
  placement?: "bottom-right" | "bottom-left" | "top-right" | "top-left";
  className?: string;
}

const PLACEMENT_CLASS: Record<NonNullable<NotificationsHostProps["placement"]>, string> = {
  "bottom-right": "af-toast-host af-pos-br",
  "bottom-left": "af-toast-host af-pos-bl",
  "top-right": "af-toast-host af-pos-tr",
  "top-left": "af-toast-host af-pos-tl",
};

export function NotificationsHost({ placement = "bottom-right", className }: NotificationsHostProps) {
  const items = useNotifications();
  if (items.length === 0) return null;
  const cls = className ? `${PLACEMENT_CLASS[placement]} ${className}` : PLACEMENT_CLASS[placement];
  return (
    <section className={cls} aria-label="Notifications">
      {items.map((n) => (
        <Notification key={n.id} n={n} />
      ))}
    </section>
  );
}
