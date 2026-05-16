"use client";

import { useEffect, useRef, useState } from "react";
import type { ChatTurn, ModelId } from "./chat.types";
import { MODELS } from "./chat.types";

interface Props {
  open: boolean;
  turns: ChatTurn[];
  modelId: ModelId;
  onClose: () => void;
  onClear: () => void;
  onSeed: (q: string) => void;
  footerModelRef: React.RefObject<HTMLSpanElement | null>;
}

const SEEDS = [
  { label: "analyze my AI exposure", q: "Analyze my exposure to AI stocks" },
  { label: "rebalance toward defensives", q: "Rebalance my equity sleeve toward defensives" },
  { label: "portfolio risk now", q: "What's my portfolio risk right now?" },
  { label: "midcap IT breakouts", q: "Scan for breakout candidates in midcap IT" },
];

export function ChatRail({
  open,
  turns,
  modelId,
  onClose,
  onClear,
  onSeed,
  footerModelRef,
}: Props) {
  const [size, setSize] = useState<"md" | "lg">("md");
  const threadRef = useRef<HTMLDivElement>(null);
  const thinking = turns.some((t) => t.loading);
  const done = !thinking && turns.length > 0 && turns[turns.length - 1]?.response != null;
  const turnCount = turns.length;

  // Scroll to bottom when new turns arrive or streaming updates land.
  const prevTurnCount = useRef(0);
  useEffect(() => {
    if (threadRef.current && (turnCount !== prevTurnCount.current || thinking)) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
      prevTurnCount.current = turnCount;
    }
  });

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && open) onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <aside
      className="chat-rail pointer-events-none absolute bottom-[62px] right-3.5 top-[10px] flex flex-col overflow-hidden rounded-[10px] border border-[color:var(--line)] opacity-0"
      style={{
        width: size === "lg" ? 680 : 480,
        maxWidth: "46%",
        background: "color-mix(in srgb, var(--surface) 94%, transparent)",
        boxShadow: "-30px 0 80px -40px rgba(0,0,0,.55), 0 12px 40px -20px rgba(0,0,0,.5)",
        backdropFilter: "blur(14px)",
        zIndex: 30,
        transform: open ? "translateX(0)" : "translateX(calc(100% + 28px))",
        opacity: open ? 1 : 0,
        pointerEvents: open ? "auto" : "none",
        transition: "transform .38s cubic-bezier(.3,.85,.4,1), opacity .25s ease, width .3s ease",
        ["--thinking" as string]: thinking ? "1" : "0",
      }}
      aria-hidden={!open}
    >
      {/* left glow stripe */}
      <div
        className="pointer-events-none absolute bottom-0 left-0 top-0 w-px"
        style={{
          background: "linear-gradient(180deg, transparent 8%, var(--accent) 50%, transparent 92%)",
          opacity: 0.55,
        }}
      />

      {/* header */}
      <header
        className="flex flex-shrink-0 items-center justify-between gap-3 border-b border-[color:var(--line)] px-4 py-3"
        style={{ background: "color-mix(in srgb, var(--surface) 60%, transparent)" }}
      >
        <div className="flex min-w-0 items-center gap-2.5">
          <div
            className="relative h-4.5 w-4.5 flex-shrink-0 rounded-full"
            style={{
              background:
                "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 25%, var(--accent) 65%, transparent)",
              boxShadow: "0 0 16px var(--glow)",
              width: 18,
              height: 18,
            }}
          />
          <div className="min-w-0">
            <div
              style={{
                fontSize: 13.5,
                fontWeight: 500,
                letterSpacing: "-0.005em",
                lineHeight: 1.1,
              }}
            >
              Alpha · Conversation
            </div>
            <div
              className="mt-0.5 flex items-center gap-1.5"
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                letterSpacing: "0.22em",
                textTransform: "uppercase",
                color: "var(--fg-3)",
              }}
            >
              <span
                className="h-1.5 w-1.5 rounded-full transition-all"
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
                }}
              />
              <span>{thinking ? "thinking…" : done ? "ready" : "idle"}</span>
              <span style={{ opacity: 0.5 }}>·</span>
              <span>
                {turnCount} turn{turnCount !== 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </div>
        <div className="flex flex-shrink-0 items-center gap-1.5">
          <CrBtn
            title={size === "lg" ? "Shrink" : "Expand"}
            onClick={() => setSize((s) => (s === "md" ? "lg" : "md"))}
          >
            ⤢
          </CrBtn>
          <CrBtn title="Clear thread" onClick={onClear}>
            ↻
          </CrBtn>
          <CrBtn title="Close" onClick={onClose}>
            ✕
          </CrBtn>
        </div>
      </header>

      {/* thread */}
      <div
        ref={threadRef}
        className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4"
        style={{ scrollbarWidth: "thin", scrollbarColor: "var(--line-hi) transparent" }}
      >
        {turns.length === 0 ? (
          <EmptyState onSeed={onSeed} />
        ) : (
          turns.map((turn) => <TurnPair key={turn.id} turn={turn} modelId={modelId} />)
        )}
      </div>

      {/* footer */}
      <div
        className="flex flex-shrink-0 items-center justify-between border-t border-[color:var(--line)] px-4 py-2"
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          color: "var(--fg-3)",
          background: "color-mix(in srgb, var(--surface) 70%, transparent)",
        }}
      >
        <span>⏎ submit · ⇧⏎ newline · ESC close</span>
        <span ref={footerModelRef} style={{ color: "var(--accent)", opacity: 0.7 }}>
          Auto → Forge Pro · streaming
        </span>
      </div>
    </aside>
  );
}

function CrBtn({
  children,
  title,
  onClick,
}: {
  children: React.ReactNode;
  title: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className="grid place-items-center rounded-[5px] border border-[color:var(--line)] transition-colors hover:border-[color:var(--accent)] hover:text-[color:var(--fg)]"
      style={{
        width: 26,
        height: 26,
        fontSize: 12,
        color: "var(--fg-3)",
        background: "transparent",
        cursor: "pointer",
      }}
      title={title}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function EmptyState({ onSeed }: { onSeed: (q: string) => void }) {
  return (
    <div
      className="flex flex-col items-center gap-2.5 px-4 py-9 text-center"
      style={{ color: "var(--fg-3)" }}
    >
      <div
        style={{
          width: 54,
          height: 54,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 22%, var(--accent) 60%, transparent 85%)",
          boxShadow: "0 0 36px var(--glow)",
          animation: "breathe 4s ease-in-out infinite",
        }}
      />
      <div
        style={{
          fontSize: 17,
          color: "var(--fg)",
          fontWeight: 500,
          letterSpacing: "-0.01em",
          marginTop: 6,
        }}
      >
        Ask Alpha anything
      </div>
      <div style={{ fontSize: 12, color: "var(--fg-3)", maxWidth: 280, lineHeight: 1.5 }}>
        analysis, rebalancing, risk, market scans — type or speak from the bar below
      </div>
      <div className="mt-3.5 flex flex-wrap justify-center gap-1.5">
        {SEEDS.map((s) => (
          <button
            key={s.label}
            type="button"
            className="fu-chip rounded-[14px] border border-dashed px-2.5 py-1 text-left transition-colors"
            style={{
              fontFamily: "Space Grotesk, sans-serif",
              fontSize: 11,
              fontStyle: "italic",
              borderColor: "var(--line-hi)",
              color: "var(--fg-2)",
              background: "transparent",
              cursor: "pointer",
            }}
            onClick={() => onSeed(s.q)}
          >
            <span
              style={{
                color: "var(--accent)",
                fontStyle: "normal",
                fontWeight: 700,
                marginRight: 4,
              }}
            >
              ›
            </span>
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function TurnPair({ turn, modelId }: { turn: ChatTurn; modelId: ModelId }) {
  const modelName =
    modelId === "auto"
      ? `Auto → ${MODELS[turn.resolvedModel].name}`
      : (MODELS[turn.resolvedModel]?.name ?? "Alpha");

  return (
    <>
      {/* user bubble */}
      <div
        className="self-end rounded-[12px_12px_4px_12px] border px-3 py-2"
        style={{
          maxWidth: "88%",
          background: "color-mix(in srgb, var(--accent) 14%, transparent)",
          borderColor: "color-mix(in srgb, var(--accent) 35%, transparent)",
          color: "var(--fg)",
          fontSize: 13,
          lineHeight: 1.5,
          fontStyle: "italic",
          letterSpacing: "0.005em",
          animation: "turnIn .25s ease-out",
        }}
      >
        {turn.query}
      </div>

      {/* alpha reply */}
      <div
        className="relative flex flex-col gap-2.5 rounded-[10px] border border-[color:var(--line)] px-3.5 py-3"
        style={{
          background: "color-mix(in srgb, var(--surface) 60%, transparent)",
          animation: "turnIn .3s ease-out",
        }}
      >
        {/* left accent bar */}
        <div
          className="pointer-events-none absolute bottom-3.5 left-0 top-3.5 w-0.5 rounded-px"
          style={{
            background: "linear-gradient(180deg, transparent, var(--accent), transparent)",
            opacity: 0.7,
          }}
        />
        {/* meta row */}
        <div
          className="flex items-center gap-2"
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 9,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--fg-3)",
          }}
        >
          <span style={{ color: "var(--accent)", fontWeight: 700 }}>ALPHA</span>
          <span>·</span>
          <span className="ml-auto">
            {turn.loading
              ? `thinking · ${modelName}`
              : `${turn.tokens ?? 0} tok · ${modelName}${turn.elapsed != null ? ` · ${turn.elapsed.toFixed(1)}s` : ""}`}
          </span>
        </div>

        {/* body */}
        <div style={{ color: "var(--fg)", fontSize: 13.5, lineHeight: 1.6 }}>
          {turn.loading && !turn.response ? (
            <TypingIndicator />
          ) : turn.error ? (
            <span style={{ color: "var(--red)", fontSize: 12 }}>Error: {turn.error}</span>
          ) : (
            <ResponseBody text={turn.response ?? ""} />
          )}
        </div>
      </div>
    </>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-1 py-1.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="rounded-full"
          style={{
            width: 5,
            height: 5,
            background: "var(--accent)",
            opacity: 0.4,
            animation: `rtBlink 1.2s ease-in-out ${i * 0.15}s infinite`,
          }}
        />
      ))}
    </div>
  );
}

// ── Inline token renderer ─────────────────────────────────────────────────
// Parses **bold**, *italic*, and `code` spans within a text segment.
// Uses no dangerouslySetInnerHTML — every node is a React element.
function InlineTokens({ text }: { text: string }) {
  // Split on **bold**, *italic*, `code` — keep delimiters via capture groups
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/);
  return (
    <>
      {parts.map((part) => {
        const k = `tok:${part.slice(0, 20)}`;
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

// ── Block renderer ─────────────────────────────────────────────────────────
// Converts markdown lines into React nodes. No eval, no HTML injection.
function ResponseBody({ text }: { text: string }) {
  const lines = text.split("\n");
  const nodes: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];

    // Fenced code block
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

    // H2
    if (/^## /.test(raw)) {
      nodes.push(
        <h2 key={i} className="rb-h2">
          <InlineTokens text={raw.slice(3)} />
        </h2>,
      );
      i++;
      continue;
    }

    // H3
    if (/^### /.test(raw)) {
      nodes.push(
        <h3 key={i} className="rb-h3">
          <InlineTokens text={raw.slice(4)} />
        </h3>,
      );
      i++;
      continue;
    }

    // Horizontal rule
    if (/^---+$/.test(raw.trim())) {
      nodes.push(<hr key={i} className="rb-hr" />);
      i++;
      continue;
    }

    // Bullet list — collect contiguous items
    if (/^[-*] /.test(raw)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*] /.test(lines[i])) {
        items.push(lines[i].slice(2));
        i++;
      }
      nodes.push(
        <ul key={i} className="rb-ul">
          {items.map((item) => (
            <li key={`ul:${item.slice(0, 24)}`}>
              <InlineTokens text={item} />
            </li>
          ))}
        </ul>,
      );
      continue;
    }

    // Numbered list — collect contiguous items
    if (/^\d+\. /.test(raw)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ""));
        i++;
      }
      nodes.push(
        <ol key={i} className="rb-ol">
          {items.map((item) => (
            <li key={`ol:${item.slice(0, 24)}`}>
              <InlineTokens text={item} />
            </li>
          ))}
        </ol>,
      );
      continue;
    }

    // Empty line → spacing gap (no <p> for blank lines)
    if (raw.trim() === "") {
      nodes.push(<div key={i} className="rb-gap" />);
      i++;
      continue;
    }

    // Paragraph
    nodes.push(
      <p key={i} className="rb-p">
        <InlineTokens text={raw} />
      </p>,
    );
    i++;
  }

  return <div className="response-body">{nodes}</div>;
}
