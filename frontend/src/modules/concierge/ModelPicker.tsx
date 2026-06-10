"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { PROVIDER_ORDER, PROVIDERS, type ProviderId } from "./concierge.providers";
import { resolveProviderAuto, resolveTopAuto } from "./concierge.routing";
import { activeModelFor, type ModelChoice } from "./concierge.types";
import { AutoRow, ModelRow, ProvRow } from "./ModelPicker.rows";
import { styles } from "./ModelPicker.styles";

interface Props {
  value: ModelChoice;
  query: string;
  onChange: (c: ModelChoice) => void;
  footerRef?: React.RefObject<HTMLSpanElement | null>;
}

export function ModelPicker({ value, query, onChange, footerRef }: Props) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<{ bottom: number; right: number; maxHeight: number } | null>(null);
  const initialFocus: ProviderId = value.provider === "auto" ? "gemini" : value.provider;
  const [focused, setFocused] = useState<ProviderId>(initialFocus);
  const btnRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const active = activeModelFor(value, query);

  useEffect(() => {
    if (footerRef?.current) {
      footerRef.current.textContent =
        active.autoLevel === "top"
          ? `Auto → ${active.modelName} · streaming`
          : active.autoLevel === "provider"
            ? `${active.providerName} / Auto → ${active.modelName} · streaming`
            : `${active.providerName} · ${active.modelName} · streaming`;
    }
  }, [active.autoLevel, active.modelName, active.providerName, footerRef]);

  useEffect(() => {
    if (!open || !btnRef.current) return;
    const r = btnRef.current.getBoundingClientRect();
    const MENU_WIDTH = 560;
    const right = Math.min(
      window.innerWidth - r.right,
      window.innerWidth - MENU_WIDTH - 117, // keep left edge ≥ 8px from viewport
    );
    setPos({ bottom: window.innerHeight - r.top + 8, right, maxHeight: Math.max(160, r.top - 16) });
    if (value.provider !== "auto") setFocused(value.provider);
  }, [open, value]);

  useEffect(() => {
    function onMouseDown(e: MouseEvent) {
      if (btnRef.current?.contains(e.target as Node)) return;
      if (menuRef.current?.contains(e.target as Node)) return;
      setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && open) setOpen(false);
    }
    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const focusedProv = PROVIDERS[focused];
  const focusedAutoResolved = resolveProviderAuto(focused, query);
  const topAuto = resolveTopAuto(query);

  return (
    <div
      data-component="ModelPicker"
      style={{ position: "relative", display: "flex", alignItems: "center", flexShrink: 0 }}
    >
      <button
        ref={btnRef}
        type="button"
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((o) => !o);
        }}
        style={{
          ...styles.btn,
          color: open ? "var(--fg)" : "var(--fg-2)",
          borderColor: open ? "color-mix(in srgb, var(--accent) 50%, transparent)" : "var(--line)",
          background: open
            ? "color-mix(in srgb, var(--accent) 8%, transparent)"
            : "color-mix(in srgb, var(--surface-lo) 70%, transparent)",
        }}
      >
        <span style={styles.dot} />
        <span
          style={{
            display: "inline-flex",
            alignItems: "baseline",
            gap: 6,
            lineHeight: 1,
            maxWidth: 240,
            overflow: "hidden",
          }}
        >
          {active.autoLevel !== "top" && (
            <span
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                letterSpacing: "0.16em",
                color: "var(--fg-3)",
                textTransform: "uppercase",
              }}
            >
              {active.providerName} /
            </span>
          )}
          <span
            style={{
              fontSize: 11,
              fontWeight: 500,
              color: "var(--fg)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {active.autoLevel === "none" ? active.modelName : "Auto"}
          </span>
          {active.autoLevel !== "none" && (
            <span
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                color: "var(--fg-3)",
                whiteSpace: "nowrap",
              }}
            >
              → {active.modelName}
            </span>
          )}
        </span>
        <svg
          width={10}
          height={10}
          viewBox="0 0 12 12"
          aria-label="Toggle menu"
          role="img"
          style={{
            color: open ? "var(--accent)" : "var(--fg-3)",
            transform: open ? "rotate(180deg)" : undefined,
            transition: "transform .2s",
          }}
        >
          <title>Toggle menu</title>
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
        pos &&
        createPortal(
          <div
            ref={menuRef}
            role="dialog"
            aria-label="Model"
            style={{
              ...styles.menu,
              bottom: pos.bottom,
              right: pos.right,
              maxHeight: pos.maxHeight,
            }}
          >
            <div style={styles.grid}>
              <div style={styles.col}>
                <div style={styles.colHead}>
                  <span>Provider</span>
                  <span style={{ opacity: 0.55 }}>{PROVIDER_ORDER.length}</span>
                </div>
                <div style={styles.colBody}>
                  <AutoRow
                    title="Auto"
                    desc="Routes across all providers per query."
                    arrow={`→ ${PROVIDERS[topAuto.provider].glyph}`}
                    selected={value.provider === "auto"}
                    onClick={() => {
                      onChange({ provider: "auto" });
                      setOpen(false);
                    }}
                  />
                  {PROVIDER_ORDER.map((pid) => (
                    <ProvRow
                      key={pid}
                      p={PROVIDERS[pid]}
                      focused={focused === pid}
                      hasSelection={value.provider === pid}
                      onHover={() => setFocused(pid)}
                      onClick={() => setFocused(pid)}
                    />
                  ))}
                </div>
              </div>

              <div style={{ ...styles.col, ...styles.colDivider }}>
                <div style={styles.colHead}>
                  <span>{focusedProv.name} models</span>
                  <span style={{ opacity: 0.55 }}>{focusedProv.models.length + 1} opts</span>
                </div>
                <div style={styles.colBody}>
                  <AutoRow
                    title={`Auto · ${focusedProv.name}`}
                    desc={focusedProv.desc}
                    arrow={`→ ${PROVIDERS[focused].models.find((m) => m.id === focusedAutoResolved)?.name ?? focusedAutoResolved}`}
                    selected={
                      value.provider === focused && (value as { model?: string }).model === "auto"
                    }
                    onClick={() => {
                      onChange({ provider: focused, model: "auto" });
                      setOpen(false);
                    }}
                  />
                  {focusedProv.models.map((m) => (
                    <ModelRow
                      key={m.id}
                      m={m}
                      selected={
                        value.provider === focused && (value as { model?: string }).model === m.id
                      }
                      onClick={() => {
                        onChange({ provider: focused, model: m.id });
                        setOpen(false);
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div style={styles.foot}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                <span
                  style={{
                    width: 5,
                    height: 5,
                    borderRadius: "50%",
                    background: "var(--green)",
                    boxShadow: "0 0 6px var(--green)",
                  }}
                />
                <span>
                  {active.autoLevel === "top"
                    ? `routing → ${active.providerName} · ${active.modelName}`
                    : active.autoLevel === "provider"
                      ? `routing within ${active.providerName} → ${active.modelName}`
                      : `pinned · ${active.providerName} · ${active.modelName}`}
                </span>
              </span>
              <span style={{ opacity: 0.7 }}>↵ select</span>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}
