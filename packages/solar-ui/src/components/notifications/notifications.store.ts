"use client";

import { useSyncExternalStore } from "react";
import type { Notification, NotificationInput, Severity } from "./notifications.types";

const MAX_STACK = 5;

let counter = 0;
let items: Notification[] = [];
const listeners = new Set<() => void>();

function emit() {
  for (const l of listeners) l();
}

function nextId(): string {
  counter += 1;
  return `n${Date.now().toString(36)}${counter.toString(36)}`;
}

function defaultTtl(sev: Severity, hasActions: boolean): number {
  if (sev === "err") return 0; // errors persist until dismissed
  if (sev === "sync") return 0; // sync resolves explicitly via update/dismiss
  if (hasActions) return 8000; // give the user time to act
  return 5000;
}

export function pushNotification(input: NotificationInput): string {
  const id = input.id ?? nextId();
  const severity = input.severity ?? "info";
  const next: Notification = {
    ...input,
    id,
    severity,
    dismissible: input.dismissible ?? true,
    ttl: input.ttl ?? defaultTtl(severity, !!input.actions?.length),
    createdAt: Date.now(),
  };
  const existing = items.findIndex((n) => n.id === id);
  if (existing >= 0) {
    items = items.map((n, i) => (i === existing ? next : n));
  } else {
    items = [...items, next].slice(-MAX_STACK);
  }
  emit();
  return id;
}

export function dismissNotification(id: string): void {
  const before = items.length;
  items = items.filter((n) => n.id !== id);
  if (items.length !== before) emit();
}

export function clearNotifications(): void {
  if (items.length === 0) return;
  items = [];
  emit();
}

function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

const getSnapshot = () => items;
const getServerSnapshot = () => [] as Notification[];

export function useNotifications(): Notification[] {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
