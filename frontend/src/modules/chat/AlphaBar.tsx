"use client";

import { useEffect, useRef, useState } from "react";
import { type ModelId, resolveAutoModel } from "./chat.types";
import { ModelPicker } from "./ModelPicker";

type Mode = "voice" | "chat";

const VOICE_PROMPTS = [
  '"Alpha, analyze my exposure to AI stocks"',
  '"Show banking drag this week"',
  '"Rebalance equity down 5% to target"',
  '"Screener: breakouts under ₹500"',
];

interface Props {
  onSubmit: (query: string, model: ModelId) => void;
  footerModelRef: React.RefObject<HTMLSpanElement | null>;
}

export function AlphaBar({ onSubmit, footerModelRef }: Props) {
  const [mode, setMode] = useState<Mode>(() => {
    try {
      return (localStorage.getItem("af-mode") as Mode) ?? "voice";
    } catch {
      return "voice";
    }
  });
  const [model, setModel] = useState<ModelId>(() => {
    try {
      return (localStorage.getItem("af-model") as ModelId) ?? "auto";
    } catch {
      return "auto";
    }
  });
  const [query, setQuery] = useState("");
  const [promptIdx, setPromptIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const id = setInterval(() => setPromptIdx((i) => (i + 1) % VOICE_PROMPTS.length), 3800);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("af-mode", mode);
    } catch {}
  }, [mode]);

  useEffect(() => {
    try {
      localStorage.setItem("af-model", model);
    } catch {}
  }, [model]);

  function handleModeChange(m: Mode) {
    setMode(m);
    if (m === "chat") {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }

  function handleSubmit() {
    const q = query.trim();
    if (!q) return;
    onSubmit(q, model);
    setQuery("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  const resolved = model === "auto" ? resolveAutoModel(query) : model;

  return (
    <footer
      data-mode={mode}
      className="relative flex flex-none items-center gap-4 rounded-[8px] border border-[color:var(--line)] px-3.5 py-1.5 min-h-[36px]"
      style={{
        background: "color-mix(in srgb, var(--surface) 82%, transparent)",
        backdropFilter: "blur(18px)",
      }}
    >
      {/* left accent stripe */}
      <div
        className="pointer-events-none absolute left-0 top-0 h-full w-0.5"
        style={{
          background: "linear-gradient(180deg, transparent, var(--accent), transparent)",
          opacity: 0.5,
        }}
      />

      {/* Voice / Chat segmented toggle */}
      <div
        className="flex flex-shrink-0 overflow-hidden rounded-[5px] border border-[color:var(--line-hi)]"
        role="tablist"
        aria-label="Input mode"
      >
        <ModeBtn
          active={mode === "voice"}
          onClick={() => handleModeChange("voice")}
          aria-label="Voice mode"
        >
          <MicIcon />
          <span>Voice</span>
        </ModeBtn>
        <ModeBtn
          active={mode === "chat"}
          onClick={() => handleModeChange("chat")}
          aria-label="Chat mode"
          style={{ borderLeft: "1px solid var(--line-hi)" }}
        >
          <ChatIcon />
          <span>Chat</span>
        </ModeBtn>
      </div>

      {/* Voice center */}
      {mode === "voice" && (
        <div className="flex min-w-0 flex-1 items-center gap-3.5">
          <div className="flex flex-shrink-0 items-center gap-2">
            <span
              className="font-medium italic leading-none"
              style={{ color: "var(--accent)", fontSize: 12, letterSpacing: "0.04em" }}
            >
              Listening…
            </span>
            <span
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                letterSpacing: "0.22em",
                textTransform: "uppercase",
                color: "var(--fg-3)",
              }}
            >
              · NEURAL INTERFACE
            </span>
          </div>
          <Waveform />
          <span
            className="flex-1 truncate italic leading-none"
            style={{ fontSize: 12, color: "var(--fg-2)", marginLeft: 4 }}
          >
            {VOICE_PROMPTS[promptIdx]}
          </span>
        </div>
      )}

      {/* Chat center */}
      {mode === "chat" && (
        <div className="flex min-w-0 flex-1 items-center gap-2.5">
          <span
            style={{
              fontFamily: "Space Mono, monospace",
              fontSize: 12,
              color: "var(--accent)",
              flexShrink: 0,
            }}
          >
            ›_
          </span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="min-w-0 flex-1 bg-transparent outline-none"
            style={{
              fontFamily: "Space Grotesk, sans-serif",
              fontSize: 13,
              color: "var(--fg)",
              caretColor: "var(--accent)",
            }}
            placeholder="Ask Alpha — e.g. rebalance my equity sleeve toward defensives"
            autoComplete="off"
            spellCheck={false}
          />
          <ModelPicker
            value={model}
            query={query}
            onChange={(id) => setModel(id)}
            footerRef={footerModelRef}
          />
          <div className="flex flex-shrink-0 gap-1">
            <Kbd>⌘</Kbd>
            <Kbd>↵</Kbd>
          </div>
        </div>
      )}

      {/* Deploy button */}
      <button
        className="flex-shrink-0 rounded-[6px] font-mono font-bold uppercase"
        style={{
          background: "linear-gradient(45deg, var(--accent), var(--accent-soft))",
          color: "var(--on-accent)",
          padding: "6px 14px",
          fontSize: 10,
          letterSpacing: "0.22em",
          boxShadow: "0 0 24px var(--glow)",
          transition: "transform .2s, box-shadow .2s",
        }}
        onClick={() => {
          if (mode === "chat") handleSubmit();
          else onSubmit(VOICE_PROMPTS[promptIdx].replace(/^"|"$/g, ""), model);
        }}
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.transform = "translateY(-1px)";
          (e.target as HTMLElement).style.boxShadow = "0 0 40px var(--glow), 0 4px 12px rgba(0,0,0,.2)";
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.transform = "";
          (e.target as HTMLElement).style.boxShadow = "0 0 24px var(--glow)";
        }}
      >
        Deploy ▸
      </button>
    </footer>
  );
}

function ModeBtn({
  active,
  onClick,
  children,
  style,
  "aria-label": ariaLabel,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  style?: React.CSSProperties;
  "aria-label": string;
}) {
  return (
    <button
      className="inline-flex items-center gap-1 px-2 py-1 transition-colors"
      style={{
        fontSize: 10,
        letterSpacing: "0.06em",
        color: active ? "var(--on-accent)" : "var(--fg-3)",
        background: active
          ? "var(--accent)"
          : "transparent",
        boxShadow: active ? "0 0 18px var(--glow)" : "none",
        borderRight: "none",
        cursor: "pointer",
        ...style,
      }}
      role="tab"
      aria-selected={active}
      aria-label={ariaLabel}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function Waveform() {
  return (
    <div className="flex flex-shrink-0 items-center gap-0.5" style={{ height: 16 }}>
      {Array.from({ length: 8 }, (_, i) => (
        <div
          key={i}
          style={{
            width: 2,
            background: "var(--accent)",
            animation: `vbar .9s ease-in-out ${i * 0.1}s infinite`,
            borderRadius: 1,
          }}
        />
      ))}
    </div>
  );
}

function MicIcon() {
  return (
    <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="9" y="3" width="6" height="12" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0" />
      <path d="M12 18v3M8 21h8" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M4 5h16v11H8l-4 4z" />
      <path d="M8 10h8M8 13h5" />
    </svg>
  );
}

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="rounded-[3px] border border-[color:var(--line-hi)] px-1 py-px leading-none"
      style={{
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.06em",
        color: "var(--fg-3)",
        background: "color-mix(in srgb, var(--surface) 50%, transparent)",
      }}
    >
      {children}
    </span>
  );
}
