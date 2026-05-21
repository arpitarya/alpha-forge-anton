"use client";

import { useEffect, useRef, useState } from "react";
import type { ChatTurn, ModelId } from "./chat.types";
import { MODELS } from "./chat.types";
import { ModelPicker } from "./ModelPicker";

interface Props {
  open: boolean;
  turns: ChatTurn[];
  modelId: ModelId;
  onClose: () => void;
  onClear: () => void;
  onSeed: (q: string) => void;
  onModelChange: (m: ModelId) => void;
  footerModelRef: React.RefObject<HTMLSpanElement | null>;
  query: string;
}

const SEEDS = [
  {
    icon: (
      <svg
        viewBox="0 0 24 24"
        width={16}
        height={16}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.7}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-label="Bar chart"
      >
        <path d="M3 13h4v8H3zM10 5h4v16h-4zM17 9h4v12h-4z" />
      </svg>
    ),
    q: "Analyze my exposure to AI stocks",
    label: "Analyze AI exposure",
    sub: "How concentrated are your holdings?",
  },
  {
    icon: (
      <svg
        viewBox="0 0 24 24"
        width={16}
        height={16}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.7}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-label="Rebalance"
      >
        <path d="M21 12a9 9 0 1 1-3-6.7M21 4v5h-5" />
      </svg>
    ),
    q: "Rebalance my equity sleeve toward defensives",
    label: "Rebalance toward defensives",
    sub: "Draft a plan I can confirm before deploy.",
  },
  {
    icon: (
      <svg
        viewBox="0 0 24 24"
        width={16}
        height={16}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.7}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-label="Risk warning"
      >
        <path d="M12 3 2 21h20zM12 9v5M12 17h.01" />
      </svg>
    ),
    q: "What's my portfolio risk right now?",
    label: "Portfolio risk right now",
    sub: "Drawdown, VaR, exposure heatmap.",
  },
  {
    icon: (
      <svg
        viewBox="0 0 24 24"
        width={16}
        height={16}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.7}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-label="Search"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
    ),
    q: "Scan for breakout candidates in midcap IT",
    label: "Midcap IT breakouts",
    sub: "Scan with ML screener, sort by confidence.",
  },
];

export function ChatRail({
  open,
  turns,
  modelId,
  onClose,
  onClear,
  onSeed,
  onModelChange,
  footerModelRef,
}: Props) {
  const [size, setSize] = useState<"md" | "lg">("md");
  const [inputValue, setInputValue] = useState("");
  const threadRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const thinking = turns.some((t) => t.loading);
  const done = !thinking && turns.length > 0 && turns[turns.length - 1]?.response != null;
  const turnCount = turns.length;

  // Scroll thread to bottom on new turns / streaming
  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  });

  // Focus textarea when rail opens
  useEffect(() => {
    if (open) {
      setTimeout(() => textareaRef.current?.focus(), 80);
    }
  }, [open]);

  // Escape closes
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && open) onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  function handleSubmit() {
    const q = inputValue.trim();
    if (!q) return;
    onSeed(q);
    setInputValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function autoGrow(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  const w = size === "lg" ? "min(1100px, calc(100vw - 40px))" : "min(820px, calc(100vw - 40px))";

  return (
    <>
      {/* Backdrop */}
      <div
        aria-hidden="true"
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          background:
            "radial-gradient(ellipse at 60% 50%, rgba(0,0,0,.52) 0%, rgba(0,0,0,.68) 100%)",
          zIndex: 28,
          opacity: open ? 1 : 0,
          pointerEvents: open ? "auto" : "none",
          transition: "opacity .3s ease",
          cursor: "pointer",
        }}
      />

      <aside
        style={{
          position: "fixed",
          left: "50%",
          bottom: 80,
          top: 16,
          width: w,
          transform: open
            ? "translateX(-50%) translateY(0)"
            : "translateX(-50%) translateY(calc(100% + 60px))",
          opacity: open ? 1 : 0,
          pointerEvents: open ? "auto" : "none",
          transition: "transform .42s cubic-bezier(.3,.85,.4,1), opacity .28s ease, width .3s ease",
          zIndex: 30,
          display: "flex",
          flexDirection: "column",
          borderRadius: 18,
          border: "1px solid var(--line)",
          overflow: "hidden",
          background: "color-mix(in srgb, var(--surface) 94%, transparent)",
          boxShadow:
            "0 30px 80px -20px rgba(0,0,0,.65), 0 0 0 1px color-mix(in srgb, var(--accent) 18%, transparent)",
          backdropFilter: "blur(20px)",
        }}
        aria-hidden={!open}
        aria-label="Alpha chat"
      >
        {/* top accent crown */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 2,
            zIndex: 2,
            pointerEvents: "none",
            background:
              "linear-gradient(90deg, transparent 5%, var(--accent) 40%, color-mix(in srgb, var(--accent) 55%, transparent) 70%, transparent 95%)",
            opacity: 0.8,
          }}
        />

        {/* ── Header ── */}
        <header
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            padding: "14px 18px",
            borderBottom: "1px solid var(--line)",
            flexShrink: 0,
            background: "color-mix(in srgb, var(--surface) 60%, transparent)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 14, minWidth: 0, flex: 1 }}>
            <OrbAvatar size={36} pulse={thinking} />
            <div style={{ minWidth: 0 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 500,
                  letterSpacing: "-0.005em",
                  lineHeight: 1.1,
                }}
              >
                Alpha · Conversation
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginTop: 4,
                  fontFamily: "Space Mono, monospace",
                  fontSize: 9,
                  letterSpacing: "0.22em",
                  textTransform: "uppercase",
                  color: "var(--fg-3)",
                }}
              >
                <span
                  style={{
                    width: 5,
                    height: 5,
                    borderRadius: "50%",
                    background: thinking ? "var(--accent)" : done ? "var(--green)" : "var(--fg-4)",
                    boxShadow: thinking
                      ? "0 0 8px var(--glow)"
                      : done
                        ? "0 0 8px rgba(55,209,122,.5)"
                        : "none",
                    display: "inline-block",
                    transition: "all .3s",
                  }}
                />
                <span>{thinking ? "thinking…" : done ? "ready" : "idle"}</span>
                <span style={{ opacity: 0.3 }}>·</span>
                <span>
                  {turnCount} turn{turnCount !== 1 ? "s" : ""}
                </span>
              </div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 4, flexShrink: 0 }}>
            <CrBtn
              title={size === "lg" ? "Shrink" : "Expand"}
              onClick={() => setSize((s) => (s === "md" ? "lg" : "md"))}
            >
              ⤢
            </CrBtn>
            <CrBtn title="Clear thread" onClick={onClear}>
              ↻
            </CrBtn>
            <CrBtn title="Close" onClick={onClose} danger>
              ✕
            </CrBtn>
          </div>
        </header>

        {/* ── Thread ── */}
        <div
          ref={threadRef}
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "20px 22px",
            display: "flex",
            flexDirection: "column",
            gap: 18,
            scrollbarWidth: "thin",
            scrollbarColor: "var(--line-hi) transparent",
          }}
        >
          {turns.length === 0 ? (
            <EmptyState onSeed={onSeed} />
          ) : (
            turns.map((turn) => (
              <TurnPair key={turn.id} turn={turn} modelId={modelId} thinking={thinking} />
            ))
          )}
        </div>

        {/* ── Docked composer ── */}
        <div
          style={{
            flexShrink: 0,
            display: "flex",
            flexDirection: "column",
            gap: 10,
            padding: "14px 20px 16px",
            borderTop: "1px solid var(--line)",
            background:
              "linear-gradient(180deg, transparent, color-mix(in srgb, var(--surface) 92%, transparent) 40%)",
            borderRadius: "0 0 18px 18px",
          }}
        >
          {/* composer card */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 0,
              padding: "12px 14px",
              background: "color-mix(in srgb, var(--surface-lo) 55%, transparent)",
              border: "1px solid var(--line)",
              borderRadius: 10,
              transition: "border-color .2s, box-shadow .2s",
            }}
            className="cr-composer-card"
          >
            {/* Row 1: prefix + textarea */}
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10, minWidth: 0 }}>
              <span
                style={{
                  fontFamily: "Space Mono, monospace",
                  fontSize: 13,
                  letterSpacing: "0.06em",
                  color: "var(--accent)",
                  flexShrink: 0,
                  fontWeight: 700,
                  paddingTop: 2,
                  lineHeight: 1.4,
                }}
              >
                ›_
              </span>
              <textarea
                ref={textareaRef}
                id="chatinput"
                value={inputValue}
                rows={2}
                onChange={(e) => {
                  setInputValue(e.target.value);
                  autoGrow(e.target);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Ask Alpha — e.g. rebalance my equity sleeve toward defensives"
                autoComplete="off"
                spellCheck={false}
                style={{
                  flex: 1,
                  minWidth: 0,
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  resize: "none",
                  fontFamily: "Space Grotesk, sans-serif",
                  fontSize: 14,
                  color: "var(--fg)",
                  caretColor: "var(--accent)",
                  lineHeight: 1.5,
                  minHeight: 44,
                  maxHeight: 160,
                  overflow: "hidden",
                  scrollbarWidth: "thin",
                  scrollbarColor: "color-mix(in srgb, var(--fg) 12%, transparent) transparent",
                }}
              />
            </div>

            {/* Row 2: toolbar */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 10,
                paddingTop: 8,
                borderTop: "1px dashed color-mix(in srgb, var(--line-hi) 70%, transparent)",
                marginTop: 8,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0, flex: 1 }}>
                <ModelPicker
                  value={modelId}
                  query={inputValue}
                  onChange={onModelChange}
                  footerRef={footerModelRef}
                />
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
                <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                  <span
                    style={{
                      fontFamily: "Space Mono, monospace",
                      fontSize: 9,
                      letterSpacing: "0.16em",
                      textTransform: "uppercase",
                      color: "var(--fg-3)",
                      marginRight: 2,
                    }}
                  >
                    send
                  </span>
                  <Kbd>↵</Kbd>
                  <span
                    style={{
                      fontFamily: "Space Mono, monospace",
                      fontSize: 9,
                      letterSpacing: "0.16em",
                      textTransform: "uppercase",
                      color: "var(--fg-3)",
                      marginLeft: 6,
                      marginRight: 2,
                    }}
                  >
                    newline
                  </span>
                  <Kbd>⇧</Kbd>
                  <Kbd>↵</Kbd>
                </div>
                <SendButton onClick={handleSubmit} />
              </div>
            </div>
          </div>

          {/* status line */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontFamily: "Space Mono, monospace",
              fontSize: 9,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "var(--fg-3)",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span
                style={{
                  width: 5,
                  height: 5,
                  borderRadius: "50%",
                  background: "var(--accent)",
                  boxShadow: "0 0 6px var(--glow)",
                  display: "inline-block",
                  animation: "mdlPulse 2.4s ease-in-out infinite",
                }}
              />
              <span ref={footerModelRef}>Auto → Claude Sonnet 4.6 · streaming</span>
            </span>
            <span style={{ opacity: 0.6 }}>Esc close</span>
          </div>
        </div>
      </aside>
    </>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────

function OrbAvatar({ size, pulse }: { size: number; pulse?: boolean }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        flexShrink: 0,
        position: "relative",
        background:
          "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 22%, var(--accent) 60%, transparent)",
        boxShadow:
          "0 0 24px var(--glow), inset -3px -5px 10px color-mix(in srgb,var(--accent-dim) 50%, transparent), inset 3px 3px 6px rgba(255,255,255,.22)",
        animation: pulse ? "breathe 1.6s ease-in-out infinite" : undefined,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: -6,
          borderRadius: "50%",
          border: "1px solid color-mix(in srgb, var(--accent) 28%, transparent)",
          animation: "pulseRing 3s ease-in-out infinite",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: -12,
          borderRadius: "50%",
          border: "1px solid color-mix(in srgb, var(--accent) 14%, transparent)",
          animation: "pulseRing 3s ease-in-out infinite",
          animationDelay: "1s",
        }}
      />
    </div>
  );
}

function CrBtn({
  children,
  title,
  onClick,
  danger,
}: {
  children: React.ReactNode;
  title: string;
  onClick: () => void;
  danger?: boolean;
}) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      type="button"
      title={title}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 28,
        height: 28,
        display: "grid",
        placeItems: "center",
        borderRadius: 6,
        border: "1px solid var(--line)",
        fontSize: 12,
        cursor: "pointer",
        color: hovered && danger ? "#fff" : hovered ? "var(--fg)" : "var(--fg-3)",
        background:
          hovered && danger
            ? "var(--red)"
            : hovered
              ? "color-mix(in srgb, var(--fg) 6%, transparent)"
              : "transparent",
        borderColor: hovered && danger ? "var(--red)" : hovered ? "var(--line-hi)" : "var(--line)",
        transition: "all .18s",
      }}
    >
      {children}
    </button>
  );
}

function SendButton({ onClick }: { onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      type="button"
      title="Send (↵)"
      aria-label="Send message"
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        padding: "5px 12px",
        borderRadius: 6,
        background: "var(--accent)",
        color: "var(--on-accent)",
        border: "none",
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        boxShadow: hovered
          ? "0 0 22px var(--glow), 0 4px 8px rgba(0,0,0,.3)"
          : "0 0 14px var(--glow)",
        transform: hovered ? "translateY(-1px)" : "translateY(0)",
        transition: "transform .15s, box-shadow .15s",
      }}
    >
      <span>Send</span>
      <svg
        width={11}
        height={11}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M3 12l18-8-7 18-3-8-8-2z" />
      </svg>
    </button>
  );
}

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.06em",
        color: "var(--fg-3)",
        background: "color-mix(in srgb, var(--surface) 50%, transparent)",
        border: "1px solid var(--line-hi)",
        borderRadius: 3,
        padding: "1px 4px",
        lineHeight: 1,
      }}
    >
      {children}
    </span>
  );
}

function EmptyState({ onSeed }: { onSeed: (q: string) => void }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        padding: "28px 16px 16px",
        gap: 8,
        color: "var(--fg-3)",
      }}
    >
      <div
        style={{
          width: 90,
          height: 90,
          borderRadius: "50%",
          position: "relative",
          marginBottom: 4,
          background:
            "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 16%, var(--accent) 52%, color-mix(in srgb,var(--accent) 45%, transparent) 88%)",
          boxShadow:
            "0 0 70px var(--glow), 0 0 140px var(--glow), inset -10px -14px 28px color-mix(in srgb,var(--accent-dim) 50%, transparent), inset 8px 8px 16px rgba(255,255,255,.18)",
          animation: "breathe 4s ease-in-out infinite",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: -12,
            borderRadius: "50%",
            border: "1px solid color-mix(in srgb, var(--accent) 30%, transparent)",
            animation: "pulseRing 3s ease-in-out infinite",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: -24,
            borderRadius: "50%",
            border: "1px solid color-mix(in srgb, var(--accent) 14%, transparent)",
            animation: "pulseRing 3.2s ease-in-out infinite",
            animationDelay: "1.2s",
          }}
        />
      </div>

      <div
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9.5,
          letterSpacing: "0.32em",
          textTransform: "uppercase",
          color: "var(--accent)",
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          marginTop: 6,
        }}
      >
        <span
          style={{
            width: 16,
            height: 1,
            background: "currentColor",
            opacity: 0.5,
            display: "inline-block",
          }}
        />
        Alpha Forge · Online
        <span
          style={{
            width: 16,
            height: 1,
            background: "currentColor",
            opacity: 0.5,
            display: "inline-block",
          }}
        />
      </div>

      <div
        style={{
          fontSize: 24,
          fontWeight: 500,
          letterSpacing: "-0.015em",
          color: "var(--fg)",
          marginTop: 2,
          lineHeight: 1.2,
        }}
      >
        Hi. Ready when you are.
      </div>
      <div
        style={{
          fontSize: 13,
          color: "var(--fg-3)",
          maxWidth: 440,
          lineHeight: 1.55,
          fontFamily: "Space Grotesk, sans-serif",
        }}
      >
        Ask anything about your portfolio, scan markets, simulate a rebalance, or just brainstorm a
        thesis.
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
          width: "100%",
          maxWidth: 580,
          marginTop: 16,
        }}
      >
        {SEEDS.map((s) => (
          <SeedCard key={s.q} seed={s} onSeed={onSeed} />
        ))}
      </div>
    </div>
  );
}

function SeedCard({ seed, onSeed }: { seed: (typeof SEEDS)[0]; onSeed: (q: string) => void }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      type="button"
      onClick={() => onSeed(seed.q)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "grid",
        gridTemplateColumns: "34px 1fr auto",
        gap: 12,
        alignItems: "center",
        padding: "13px 14px",
        borderRadius: 11,
        textAlign: "left",
        fontFamily: "Space Grotesk, sans-serif",
        background: hovered
          ? "color-mix(in srgb, var(--accent) 6%, var(--surface-lo))"
          : "color-mix(in srgb, var(--surface-lo) 45%, transparent)",
        border: `1px solid ${hovered ? "color-mix(in srgb, var(--accent) 50%, var(--line-hi))" : "var(--line)"}`,
        color: hovered ? "var(--fg)" : "var(--fg-2)",
        cursor: "pointer",
        transform: hovered ? "translateY(-2px)" : "translateY(0)",
        boxShadow: hovered
          ? "0 10px 28px -10px color-mix(in srgb, var(--accent) 30%, transparent)"
          : "none",
        transition: "all .22s cubic-bezier(.34,1.32,.64,1)",
      }}
    >
      <span
        style={{
          width: 34,
          height: 34,
          borderRadius: 8,
          display: "grid",
          placeItems: "center",
          background: hovered
            ? "color-mix(in srgb, var(--accent) 22%, transparent)"
            : "color-mix(in srgb, var(--accent) 12%, transparent)",
          border: `1px solid ${hovered ? "color-mix(in srgb, var(--accent) 55%, transparent)" : "color-mix(in srgb, var(--accent) 30%, transparent)"}`,
          color: "var(--accent)",
          transition: "all .22s",
        }}
      >
        {seed.icon}
      </span>
      <span style={{ display: "flex", flexDirection: "column", gap: 3, minWidth: 0 }}>
        <span
          style={{
            fontSize: 13,
            fontWeight: 500,
            color: "var(--fg)",
            letterSpacing: "-0.005em",
            lineHeight: 1.2,
          }}
        >
          {seed.label}
        </span>
        <span
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 9.5,
            letterSpacing: "0.06em",
            color: "var(--fg-3)",
            lineHeight: 1.4,
          }}
        >
          {seed.sub}
        </span>
      </span>
      <span
        style={{
          color: "var(--accent)",
          fontFamily: "Space Mono, monospace",
          fontSize: 13,
          opacity: hovered ? 1 : 0.4,
          transform: hovered ? "translateX(2px)" : "translateX(0)",
          transition: "all .22s",
        }}
      >
        →
      </span>
    </button>
  );
}

function TurnPair({
  turn,
  modelId,
  thinking,
}: {
  turn: ChatTurn;
  modelId: ModelId;
  thinking: boolean;
}) {
  const modelName =
    modelId === "auto"
      ? `Auto → ${MODELS[turn.resolvedModel]?.name ?? "Alpha"}`
      : (MODELS[turn.resolvedModel]?.name ?? "Alpha");

  const now = new Date();
  const timeStr = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;

  return (
    <>
      {/* user bubble — right aligned */}
      <div
        style={{
          alignSelf: "flex-end",
          maxWidth: "78%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: 5,
          animation: "turnIn .32s cubic-bezier(.34,1.32,.46,1)",
        }}
      >
        <div
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 9,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--fg-4)",
          }}
        >
          YOU · <b style={{ color: "var(--fg-3)", fontWeight: 400 }}>{timeStr}</b>
        </div>
        <div
          style={{
            padding: "11px 16px",
            borderRadius: "14px 14px 4px 14px",
            background:
              "color-mix(in srgb, var(--accent) 12%, color-mix(in srgb, var(--surface-hi) 80%, transparent))",
            border: "1px solid color-mix(in srgb, var(--accent) 32%, var(--line-hi))",
            color: "var(--fg)",
            fontSize: 13.5,
            lineHeight: 1.55,
            letterSpacing: "0.005em",
            fontFamily: "Space Grotesk, sans-serif",
            boxShadow: "0 6px 18px -10px color-mix(in srgb, var(--accent) 25%, transparent)",
          }}
        >
          {turn.query}
        </div>
      </div>

      {/* alpha reply — orb avatar + card */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "34px 1fr",
          gap: 14,
          animation: "turnIn .35s cubic-bezier(.34,1.32,.46,1)",
        }}
      >
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            flexShrink: 0,
            alignSelf: "start",
            marginTop: 2,
            background:
              "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 22%, var(--accent) 60%, transparent)",
            boxShadow:
              "0 0 18px var(--glow), inset -3px -5px 10px color-mix(in srgb,var(--accent-dim) 50%, transparent), inset 3px 3px 6px rgba(255,255,255,.22)",
            animation: thinking && !turn.response ? "breathe 1.6s ease-in-out infinite" : undefined,
          }}
        />
        <div
          style={{
            padding: "14px 16px",
            borderRadius: "4px 14px 14px 14px",
            background: "color-mix(in srgb, var(--surface) 65%, transparent)",
            border: "1px solid var(--line)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              marginBottom: 10,
              fontFamily: "Space Mono, monospace",
              fontSize: 9,
              letterSpacing: "0.22em",
              textTransform: "uppercase",
              color: "var(--fg-3)",
            }}
          >
            <span style={{ color: "var(--accent)", fontWeight: 700 }}>ALPHA</span>
            <span>·</span>
            <span style={{ marginLeft: "auto", textTransform: "none", letterSpacing: "0.06em" }}>
              {turn.loading
                ? `thinking · ${modelName}`
                : `${turn.tokens ?? 0} tok · ${modelName}${turn.elapsed != null ? ` · ${turn.elapsed.toFixed(1)}s` : ""}`}
            </span>
          </div>
          <div
            style={{
              color: "var(--fg)",
              fontSize: 14,
              lineHeight: 1.65,
              fontFamily: "Space Grotesk, sans-serif",
            }}
          >
            {turn.loading && !turn.response ? (
              <TypingIndicator />
            ) : turn.error ? (
              <span style={{ color: "var(--red)", fontSize: 12 }}>Error: {turn.error}</span>
            ) : (
              <ResponseBody text={turn.response ?? ""} />
            )}
          </div>
        </div>
      </div>
    </>
  );
}

function TypingIndicator() {
  return (
    <div style={{ display: "flex", gap: 4, padding: "6px 0" }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: 5,
            height: 5,
            borderRadius: "50%",
            background: "var(--accent)",
            opacity: 0.4,
            animation: `rtBlink 1.2s ease-in-out ${i * 0.15}s infinite`,
            display: "inline-block",
          }}
        />
      ))}
    </div>
  );
}

function InlineTokens({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/);
  return (
    <>
      {parts.map((part, idx) => {
        const k = `tok:${idx}`;
        if (part.startsWith("**") && part.endsWith("**"))
          return (
            <strong key={k} style={{ fontWeight: 600, color: "var(--fg)" }}>
              {part.slice(2, -2)}
            </strong>
          );
        if (part.startsWith("*") && part.endsWith("*"))
          return (
            <em key={k} style={{ fontStyle: "italic", color: "var(--fg-2)" }}>
              {part.slice(1, -1)}
            </em>
          );
        if (part.startsWith("`") && part.endsWith("`"))
          return (
            <code key={k} className="rb-inline-code">
              {part.slice(1, -1)}
            </code>
          );
        return <span key={k}>{part}</span>;
      })}
    </>
  );
}

function ResponseBody({ text }: { text: string }) {
  const lines = text.split("\n");
  const nodes: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];

    if (raw.trimStart().startsWith("```")) {
      const lang = raw.trimStart().slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trimStart().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      nodes.push(
        <pre key={i} className="rb-code-block">
          {lang && <span className="rb-code-lang">{lang}</span>}
          <code>{codeLines.join("\n")}</code>
        </pre>,
      );
      i++;
      continue;
    }
    if (/^## /.test(raw)) {
      nodes.push(
        <h2 key={i} className="rb-h2">
          <InlineTokens text={raw.slice(3)} />
        </h2>,
      );
      i++;
      continue;
    }
    if (/^### /.test(raw)) {
      nodes.push(
        <h3 key={i} className="rb-h3">
          <InlineTokens text={raw.slice(4)} />
        </h3>,
      );
      i++;
      continue;
    }
    if (/^---+$/.test(raw.trim())) {
      nodes.push(<hr key={i} className="rb-hr" />);
      i++;
      continue;
    }

    if (/^[-*] /.test(raw)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*] /.test(lines[i])) {
        items.push(lines[i].slice(2));
        i++;
      }
      nodes.push(
        <ul key={i} className="rb-ul">
          {items.map((it) => (
            <li key={it.slice(0, 24)}>
              <InlineTokens text={it} />
            </li>
          ))}
        </ul>,
      );
      continue;
    }
    if (/^\d+\. /.test(raw)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ""));
        i++;
      }
      nodes.push(
        <ol key={i} className="rb-ol">
          {items.map((it) => (
            <li key={it.slice(0, 24)}>
              <InlineTokens text={it} />
            </li>
          ))}
        </ol>,
      );
      continue;
    }
    if (raw.trim() === "") {
      nodes.push(<div key={i} className="rb-gap" />);
      i++;
      continue;
    }
    nodes.push(
      <p key={i} className="rb-p">
        <InlineTokens text={raw} />
      </p>,
    );
    i++;
  }

  return <div className="response-body">{nodes}</div>;
}
