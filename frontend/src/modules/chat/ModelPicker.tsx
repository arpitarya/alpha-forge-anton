"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { MODELS, type ModelId, resolveAutoModel } from "./chat.types";

interface Props {
  value: ModelId;
  query: string;
  onChange: (id: ModelId) => void;
  footerRef?: React.RefObject<HTMLSpanElement | null>;
}

export function ModelPicker({ value, query, onChange, footerRef }: Props) {
  const [open, setOpen] = useState(false);
  const [dropPos, setDropPos] = useState<{ bottom: number; right: number } | null>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);

  const resolved = value === "auto" ? resolveAutoModel(query) : value;
  const resolvedName = MODELS[resolved].name;

  useEffect(() => {
    if (footerRef?.current) {
      footerRef.current.textContent =
        value === "auto" ? `Auto → ${resolvedName} · streaming` : `${resolvedName} · streaming`;
    }
  }, [value, resolvedName, footerRef]);

  // Position the portal dropdown above the button, aligned to its right edge.
  useEffect(() => {
    if (!open || !btnRef.current) return;
    const r = btnRef.current.getBoundingClientRect();
    setDropPos({
      bottom: window.innerHeight - r.top + 8,
      right: window.innerWidth - r.right,
    });
  }, [open]);

  // Close on outside click (covers both the trigger and the portal).
  useEffect(() => {
    function onMouseDown(e: MouseEvent) {
      const target = e.target as Node;
      if (btnRef.current?.contains(target)) return;
      if (dropRef.current?.contains(target)) return;
      setOpen(false);
    }
    document.addEventListener("mousedown", onMouseDown);
    return () => document.removeEventListener("mousedown", onMouseDown);
  }, []);

  const displayName = value === "auto" ? "Auto" : MODELS[value].name;

  return (
    <div className="mdl relative flex flex-shrink-0 items-center" data-id={value}>
      <button
        ref={btnRef}
        className="mdl-btn inline-flex h-6 items-center gap-2 rounded-[6px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface-lo)_70%,transparent)] px-2 py-0 text-[color:var(--fg-2)] transition-all hover:border-[color:var(--line-hi)] hover:text-[color:var(--fg)]"
        style={{ fontSize: 11 }}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((o) => !o);
        }}
      >
        <span
          className="h-1.5 w-1.5 flex-shrink-0 rounded-full"
          style={{
            background: "var(--accent)",
            boxShadow: "0 0 8px var(--glow)",
            animation: "mdlPulse 2.4s ease-in-out infinite",
          }}
        />
        <span className="flex items-baseline gap-1 leading-none">
          <span className="font-medium" style={{ color: "var(--fg)", fontSize: 11 }}>
            {displayName}
          </span>
          {value === "auto" && (
            <span
              className="whitespace-nowrap"
              style={{ fontFamily: "Space Mono, monospace", fontSize: 9, color: "var(--fg-3)" }}
            >
              → {resolvedName}
            </span>
          )}
        </span>
        <svg
          className="h-2.5 w-2.5 flex-shrink-0 transition-transform"
          style={{
            color: "var(--fg-3)",
            transform: open ? "rotate(180deg)" : undefined,
          }}
          viewBox="0 0 12 12"
          aria-hidden
        >
          <path
            d="M3 4.5l3 3 3-3"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {open &&
        dropPos &&
        createPortal(
          <div
            ref={dropRef}
            className="fixed w-[280px] rounded-[10px] border border-[color:var(--line-hi)] p-1.5"
            style={{
              bottom: dropPos.bottom,
              right: dropPos.right,
              zIndex: 9999,
              background: "color-mix(in srgb, var(--surface) 96%, transparent)",
              boxShadow: "0 12px 40px -8px rgba(0,0,0,.55)",
              backdropFilter: "blur(18px)",
            }}
            role="listbox"
          >
            <div
              className="px-2.5 pb-1 pt-1.5"
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                letterSpacing: "0.22em",
                color: "var(--fg-4)",
                textTransform: "uppercase",
              }}
            >
              MODEL
            </div>

            <ModelOption
              id="auto"
              name="Auto"
              badge="DEFAULT"
              description="Routes to the best model per query — shown inline."
              active={value === "auto"}
              onClick={() => {
                onChange("auto");
                setOpen(false);
              }}
            />
            <div className="my-1 mx-1.5 h-px" style={{ background: "var(--line)" }} />
            {(
              Object.entries(MODELS) as [
                Exclude<ModelId, "auto">,
                (typeof MODELS)[keyof typeof MODELS],
              ][]
            ).map(([id, meta]) => (
              <ModelOption
                key={id}
                id={id}
                name={meta.name}
                tag={meta.tag}
                description={meta.description}
                active={value === id}
                onClick={() => {
                  onChange(id);
                  setOpen(false);
                }}
              />
            ))}
          </div>,
          document.body,
        )}
    </div>
  );
}

function ModelOption({
  name,
  badge,
  tag,
  description,
  active,
  onClick,
}: {
  id: string;
  name: string;
  badge?: string;
  tag?: string;
  description: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      className="flex w-full items-start justify-between gap-2 rounded-[7px] px-2.5 py-2 text-left transition-colors"
      style={{
        background: active ? "color-mix(in srgb, var(--accent) 10%, transparent)" : "transparent",
        color: active ? "var(--fg)" : "var(--fg-2)",
      }}
      role="option"
      aria-selected={active}
      type="button"
      onClick={onClick}
    >
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span
          className="inline-flex items-center gap-1.5"
          style={{ fontSize: 12.5, fontWeight: 500, color: "var(--fg)" }}
        >
          {name}
          {badge && (
            <span
              className="rounded-[3px] border px-1 py-px"
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 8,
                letterSpacing: "0.16em",
                color: "var(--accent)",
                borderColor: "color-mix(in srgb, var(--accent) 45%, transparent)",
                background: "color-mix(in srgb, var(--accent) 8%, transparent)",
              }}
            >
              {badge}
            </span>
          )}
          {tag && (
            <span
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 8.5,
                letterSpacing: "0.12em",
                color: "var(--fg-3)",
                textTransform: "uppercase",
              }}
            >
              {tag}
            </span>
          )}
        </span>
        <span style={{ fontSize: 11, lineHeight: 1.4, color: "var(--fg-3)" }}>{description}</span>
      </div>
      {active && (
        <span
          className="flex-shrink-0 self-center"
          style={{ fontSize: 13, color: "var(--accent)" }}
        >
          ✓
        </span>
      )}
    </button>
  );
}
