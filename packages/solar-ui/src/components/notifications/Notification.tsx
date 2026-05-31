"use client";

import { useEffect, useRef, useState } from "react";
import { CloseIcon, severityIcon } from "./notifications.icons";
import { dismissNotification } from "./notifications.store";
import type { Notification as NotificationModel } from "./notifications.types";

const DEFAULT_PILL: Record<NotificationModel["severity"], string> = {
  ok: "Confirmed",
  err: "Failed",
  warn: "Warning",
  info: "Notice",
  sync: "In progress",
  neutral: "",
};

const EXIT_MS = 300;

function fmtTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
}

function fmtDateTime(ts: number): string {
  return new Date(ts).toLocaleString("en-US", {
    month: "short", day: "numeric", year: "numeric",
    hour: "numeric", minute: "2-digit", second: "2-digit", hour12: true,
  });
}

interface Props {
  n: NotificationModel;
}

export function Notification({ n }: Props) {
  const [exiting, setExiting] = useState(false);
  const exitRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const ttlRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const startTtl = () => {
    if (!n.ttl || n.ttl <= 0) return;
    ttlRef.current = setTimeout(() => beginExit(), n.ttl);
  };
  const cancelTtl = () => {
    if (ttlRef.current) {
      clearTimeout(ttlRef.current);
      ttlRef.current = null;
    }
  };

  const beginExit = () => {
    if (exiting) return;
    setExiting(true);
    exitRef.current = setTimeout(() => dismissNotification(n.id), EXIT_MS);
  };

  // biome-ignore lint/correctness/useExhaustiveDependencies: ttl-driven only; closure over n.id/exiting is intentional and stable per toast
  useEffect(() => {
    startTtl();
    return () => {
      cancelTtl();
      if (exitRef.current) clearTimeout(exitRef.current);
    };
  }, [n.ttl]);

  const pill = n.pill ?? DEFAULT_PILL[n.severity];
  const icon = n.icon ?? severityIcon(n.severity);
  const cls = `af-bn af-${n.severity}${n.indeterminate ? " af-indet" : ""}${exiting ? " af-out" : ""}`;

  return (
    // biome-ignore lint/a11y/noStaticElementInteractions: hover-pause UX nicety on a div that already carries alert/status role
    <div
      className={cls}
      role={n.severity === "err" ? "alert" : "status"}
      aria-live={n.severity === "err" ? "assertive" : "polite"}
      onMouseEnter={cancelTtl}
      onMouseLeave={startTtl}
    >
      <div className="af-ic">{icon}</div>
      <div className="af-bd">
        <div className="af-hd">
          <span className="af-ti">{n.title}</span>
          {pill ? <span className="af-pill">{pill}</span> : null}
          <span className="af-tm" title={fmtDateTime(n.createdAt)}>{fmtTime(n.createdAt)}</span>
        </div>
        {n.message ? <div className="af-ms">{n.message}</div> : null}
        {n.actions?.length ? (
          <div className="af-acts">
            {n.actions.map((a) => (
              <button
                key={a.label}
                type="button"
                className={`af-b ${a.variant ?? "line"}`}
                onClick={() => {
                  a.onClick();
                  beginExit();
                }}
              >
                {a.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>
      {n.dismissible ? (
        <button type="button" className="af-x" aria-label="Dismiss" onClick={beginExit}>
          {CloseIcon}
        </button>
      ) : null}
      {n.indeterminate ? <div className="af-prog" /> : null}
    </div>
  );
}
