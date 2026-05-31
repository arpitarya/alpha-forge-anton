"use client";

import { useEffect, useState } from "react";
import type { ModelChoice } from "./concierge.types";
import { VoiceCenter } from "./VoiceCenter";

type Mode = "voice" | "chat";

interface Props {
  onSubmit: (query: string, choice: ModelChoice) => void;
  choice: ModelChoice;
  footerModelRef: React.RefObject<HTMLSpanElement | null>;
  railOpen: boolean;
  onChatModeOpen: () => void;
}

export function AlphaBar({
  onSubmit,
  choice,
  footerModelRef: _footerModelRef,
  railOpen,
  onChatModeOpen,
}: Props) {
  const [mode, setMode] = useState<Mode>(() => {
    try {
      return (localStorage.getItem("af-mode") as Mode) ?? "voice";
    } catch {
      return "voice";
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem("af-mode", mode);
    } catch {}
  }, [mode]);

  function handleModeChange(m: Mode) {
    setMode(m);
    if (m === "chat") onChatModeOpen();
  }

  // When rail closes, reset mode to voice so bar shows voice center
  useEffect(() => {
    if (!railOpen) setMode("voice");
  }, [railOpen]);

  return (
    <footer
      className="af-voice"
      data-mode={mode}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        borderRadius: 8,
        border: "1px solid var(--line)",
        padding: "7px 14px",
        minHeight: 36,
        background: "color-mix(in srgb, var(--surface) 82%, transparent)",
        backdropFilter: "blur(18px)",
        position: "relative",
        zIndex: 45,
        transition: "padding .2s",
      }}
    >
      {/* left accent stripe */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          height: "100%",
          width: 2,
          background: "linear-gradient(180deg, transparent, var(--accent), transparent)",
          opacity: 0.5,
          pointerEvents: "none",
        }}
      />

      <ModeSegment mode={railOpen ? "chat" : mode} onChange={handleModeChange} />

      {/* Voice center — hidden when rail is open */}
      {!railOpen && mode === "voice" && (
        <VoiceCenter
          onTranscript={(text) => {
            onChatModeOpen();
            onSubmit(text, choice);
          }}
        />
      )}

      {/* Slim hint when chat rail is open */}
      {railOpen && (
        <span
          style={{
            flex: 1,
            fontFamily: "Space Mono, monospace",
            fontSize: 10,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "var(--fg-4)",
            paddingLeft: 4,
          }}
        >
          chatting with Alpha · type in the panel ↑
        </span>
      )}

      {/* Deploy button */}
      <DeployButton
        onClick={() => {
          onChatModeOpen();
          onSubmit("What's moving my portfolio right now?", choice);
        }}
      />
    </footer>
  );
}

function ModeSegment({
  mode,
  onChange,
}: {
  mode: "voice" | "chat";
  onChange: (m: "voice" | "chat") => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        flexShrink: 0,
        overflow: "hidden",
        borderRadius: 5,
        border: "1px solid var(--line-hi)",
        background: "color-mix(in srgb, var(--surface) 60%, transparent)",
      }}
      role="tablist"
      aria-label="Input mode"
    >
      <ModeBtn active={mode === "voice"} onClick={() => onChange("voice")} ariaLabel="Voice mode">
        <MicIcon />
        <span>Voice</span>
      </ModeBtn>
      <ModeBtn
        active={mode === "chat"}
        onClick={() => onChange("chat")}
        ariaLabel="Chat mode"
        borderLeft
      >
        <ChatIcon />
        <span>Chat</span>
      </ModeBtn>
    </div>
  );
}

function ModeBtn({
  active,
  onClick,
  children,
  ariaLabel,
  borderLeft,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  ariaLabel: string;
  borderLeft?: boolean;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      aria-label={ariaLabel}
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "5px 9px",
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.22em",
        textTransform: "uppercase",
        color: active ? "var(--on-accent)" : "var(--fg-3)",
        background: active ? "var(--accent)" : "transparent",
        boxShadow: active ? "0 0 18px var(--glow)" : "none",
        borderRight: borderLeft ? undefined : "1px solid var(--line)",
        borderLeft: borderLeft ? "1px solid var(--line)" : undefined,
        border: "none",
        cursor: "pointer",
        transition: "color .15s, background .15s",
      }}
    >
      {children}
    </button>
  );
}

function DeployButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      style={{
        flexShrink: 0,
        borderRadius: 6,
        fontFamily: "Space Mono, monospace",
        fontWeight: 700,
        textTransform: "uppercase",
        background: "linear-gradient(45deg, var(--accent), var(--accent-soft))",
        color: "var(--on-accent)",
        padding: "6px 14px",
        fontSize: 10,
        letterSpacing: "0.22em",
        boxShadow: "0 0 24px var(--glow)",
        border: "none",
        cursor: "pointer",
        transition: "transform .2s, box-shadow .2s",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "translateY(-1px)";
        (e.currentTarget as HTMLElement).style.boxShadow =
          "0 0 40px var(--glow), 0 4px 12px rgba(0,0,0,.2)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "";
        (e.currentTarget as HTMLElement).style.boxShadow = "0 0 24px var(--glow)";
      }}
      onClick={onClick}
    >
      Deploy ▸
    </button>
  );
}

function MicIcon() {
  return (
    <svg
      width={12}
      height={12}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="9" y="3" width="6" height="12" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0" />
      <path d="M12 18v3M8 21h8" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg
      width={12}
      height={12}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 5h16v11H8l-4 4z" />
      <path d="M8 10h8M8 13h5" />
    </svg>
  );
}
