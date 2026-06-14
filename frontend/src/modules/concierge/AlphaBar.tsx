"use client";

import { useEffect, useRef, useState } from "react";
import type { ModelChoice } from "./concierge.types";
import { ModelPicker } from "./ModelPicker";
import { useVoice } from "./useVoice";

type Mode = "voice" | "chat";

const VOICE_PROMPTS = [
  '"Alpha, analyze my AI stocks exposure…"',
  '"Show banking drag this week"',
  '"Rebalance equity down 5% to target"',
  '"Screener: breakouts under ₹500"',
];

interface Props {
  onSubmit: (query: string, choice: ModelChoice) => void;
  onChoiceChange: (c: ModelChoice) => void;
  choice: ModelChoice;
  railOpen: boolean;
  onChatModeOpen: () => void;
  onClose?: () => void;
}

export function AlphaBar({
  onSubmit,
  onChoiceChange,
  choice,
  railOpen,
  onChatModeOpen,
  onClose,
}: Props) {
  const [mode, setMode] = useState<Mode>(() => {
    try {
      return (localStorage.getItem("af-mode") as Mode) ?? "voice";
    } catch {
      return "voice";
    }
  });
  const [inputValue, setInputValue] = useState("");
  const [isMultiline, setIsMultiline] = useState(false);
  const [promptIdx, setPromptIdx] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const voice = useVoice((txt) => {
    if (txt) {
      onChatModeOpen();
      onSubmit(txt, choice);
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("af-mode", mode);
    } catch {}
  }, [mode]);
  useEffect(() => {
    if (!railOpen) setMode("voice");
  }, [railOpen]);
  useEffect(() => {
    if (voice.listening) return;
    const id = setInterval(() => setPromptIdx((i) => (i + 1) % VOICE_PROMPTS.length), 3800);
    return () => clearInterval(id);
  }, [voice.listening]);

  const voiceText = voice.transcribing
    ? "Transcribing…"
    : voice.listening
      ? voice.transcript || voice.interim || "Listening…"
      : VOICE_PROMPTS[promptIdx];

  function handleModeChange(m: Mode) {
    setMode(m);
  }

  function checkMultiline(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    setIsMultiline(el.value.trim().length > 0 && el.scrollHeight > 34);
  }

  function handleFooterSubmit() {
    const q = inputValue.trim();
    if (!q) return;
    onChatModeOpen();
    onSubmit(q, choice);
    setInputValue("");
    setIsMultiline(false);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleFooterSubmit();
    }
  }

  const footerStyle: React.CSSProperties = railOpen
    ? {
        display: "grid",
        gridTemplateColumns: "auto 1fr",
        alignItems: "center",
        gap: 10,
        padding: "9px 16px",
        minHeight: 36,
      }
    : mode === "chat" && isMultiline
      ? { display: "flex", alignItems: "stretch", gap: 12, padding: "12px 14px" }
      : { display: "flex", alignItems: "center", gap: 12, padding: "9px 14px", minHeight: 36 };

  return (
    <footer
      className="af-voice"
      style={{
        ...footerStyle,
        borderRadius: 8,
        border: "1px solid var(--line)",
        background: "color-mix(in srgb, var(--surface) 82%, transparent)",
        backdropFilter: "blur(18px)",
        position: "relative",
        zIndex: 45,
        transition: "padding .2s",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: "100%",
          height: 1,
          background: "linear-gradient(90deg, transparent, var(--accent), transparent)",
          opacity: 0.45,
          pointerEvents: "none",
        }}
      />

      <ModeSegment
        mode={railOpen ? "chat" : mode}
        onChange={handleModeChange}
        onDoubleOpen={() => {
          setMode("chat");
          onChatModeOpen();
        }}
      />

      {railOpen && <CollapsedStrip onClose={onClose} />}

      {!railOpen && mode === "voice" && (
        <VoiceBar
          voiceText={voiceText}
          choice={choice}
          query={inputValue}
          onChoiceChange={onChoiceChange}
        />
      )}

      {!railOpen && mode === "chat" && !isMultiline && (
        <ChatCommandLine
          textareaRef={textareaRef}
          inputValue={inputValue}
          onChange={(v, el) => {
            setInputValue(v);
            checkMultiline(el);
          }}
          onKeyDown={handleKeyDown}
          choice={choice}
          onChoiceChange={onChoiceChange}
        />
      )}

      {!railOpen && mode === "chat" && isMultiline && (
        <ComposeCard
          textareaRef={textareaRef}
          inputValue={inputValue}
          choice={choice}
          onChange={(v, el) => {
            setInputValue(v);
            checkMultiline(el);
          }}
          onKeyDown={handleKeyDown}
          onSubmit={handleFooterSubmit}
          onChoiceChange={onChoiceChange}
        />
      )}
    </footer>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function ModeSegment({
  mode,
  onChange,
  onDoubleOpen,
}: {
  mode: Mode;
  onChange: (m: Mode) => void;
  onDoubleOpen: () => void;
}) {
  return (
    <div
      role="tablist"
      aria-label="Input mode"
      title="Double-click to open the chat panel"
      onDoubleClick={onDoubleOpen}
      style={{
        display: "flex",
        height: 26,
        alignItems: "stretch",
        flexShrink: 0,
        overflow: "hidden",
        borderRadius: 6,
        border: "1px solid var(--line-hi)",
        background: "color-mix(in srgb, var(--surface) 60%, transparent)",
        userSelect: "none",
      }}
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
        padding: "0 10px",
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

function VoiceBar({
  voiceText,
  choice,
  query,
  onChoiceChange,
}: {
  voiceText: string;
  choice: ModelChoice;
  query: string;
  onChoiceChange: (c: ModelChoice) => void;
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, minWidth: 0, flex: 1 }}>
      <Bars />
      <span
        style={{
          flex: 1,
          minWidth: 0,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
          fontSize: 12,
          fontStyle: "italic",
          color: "var(--fg-2)",
        }}
      >
        {voiceText}
        <span
          style={{
            display: "inline-block",
            width: 1,
            height: "1em",
            background: "var(--accent)",
            verticalAlign: "-2px",
            animation: "caret 1s step-end infinite",
            marginLeft: 2,
          }}
        />
      </span>
      <ModelPicker value={choice} query={query} onChange={onChoiceChange} />
    </div>
  );
}

function ChatCommandLine({
  textareaRef,
  inputValue,
  onChange,
  onKeyDown,
  choice,
  onChoiceChange,
}: {
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  inputValue: string;
  onChange: (v: string, el: HTMLTextAreaElement) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  choice: ModelChoice;
  onChoiceChange: (c: ModelChoice) => void;
}) {
  return (
    <>
      <span
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 13,
          letterSpacing: "0.06em",
          color: "var(--accent)",
          flexShrink: 0,
          fontWeight: 700,
          lineHeight: 1.4,
        }}
      >
        ›_
      </span>
      <textarea
        id="chatinput-bar"
        ref={textareaRef}
        value={inputValue}
        rows={1}
        onChange={(e) => onChange(e.target.value, e.target)}
        onKeyDown={onKeyDown}
        placeholder="Ask Alpha — rebalance toward defensives…"
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
          fontStyle: "italic",
          color: "var(--fg)",
          caretColor: "var(--accent)",
          lineHeight: 1.4,
          minHeight: 22,
          maxHeight: 160,
          overflow: "hidden",
          padding: "2px 0",
        }}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        <Kbd>↵</Kbd>
        <ModelPicker value={choice} query={inputValue} onChange={onChoiceChange} />
      </div>
    </>
  );
}

function ComposeCard({
  textareaRef,
  inputValue,
  choice,
  onChange,
  onKeyDown,
  onSubmit,
  onChoiceChange,
}: {
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  inputValue: string;
  choice: ModelChoice;
  onChange: (v: string, el: HTMLTextAreaElement) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onSubmit: () => void;
  onChoiceChange: (c: ModelChoice) => void;
}) {
  return (
    <div
      style={{
        flex: 1,
        minWidth: 0,
        display: "flex",
        flexDirection: "column",
        padding: "11px 14px",
        background: "color-mix(in srgb, var(--surface-lo) 55%, transparent)",
        border: "1px solid var(--line-hi)",
        borderRadius: 10,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10, minWidth: 0 }}>
        <span
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 13,
            letterSpacing: "0.06em",
            color: "var(--accent)",
            flexShrink: 0,
            fontWeight: 700,
            paddingTop: 3,
            lineHeight: 1.4,
          }}
        >
          ›_
        </span>
        <textarea
          id="chatinput-bar"
          ref={textareaRef}
          value={inputValue}
          rows={1}
          onChange={(e) => onChange(e.target.value, e.target)}
          onKeyDown={onKeyDown}
          placeholder="Ask Alpha — rebalance toward defensives…"
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
            fontStyle: "italic",
            fontSize: 14,
            color: "var(--fg)",
            caretColor: "var(--accent)",
            lineHeight: 1.5,
            minHeight: 44,
            maxHeight: 160,
            overflow: "hidden",
          }}
        />
      </div>
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
        <ModelPicker value={choice} query={inputValue} onChange={onChoiceChange} />
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Kbd>↵</Kbd>
          <Kbd>⇧↵</Kbd>
          <SendButton onClick={onSubmit} />
        </div>
      </div>
    </div>
  );
}

function CollapsedStrip({ onClose }: { onClose?: () => void }) {
  return (
    <span style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0, flex: 1 }}>
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          fontFamily: "Space Mono, monospace",
          fontSize: 9.5,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          color: "var(--fg-2)",
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: "var(--accent)",
            boxShadow: "0 0 8px var(--glow)",
            animation: "mdlPulse 2.4s ease-in-out infinite",
            display: "inline-block",
            flexShrink: 0,
          }}
        />
        Chatting with Alpha · panel above
      </span>
      <button
        type="button"
        onClick={onClose}
        style={{
          marginLeft: "auto",
          fontFamily: "Space Mono, monospace",
          fontSize: 8.5,
          letterSpacing: "0.06em",
          color: "var(--fg-2)",
          border: "1px solid var(--line-hi)",
          borderRadius: 3,
          padding: "2px 6px",
          background: "transparent",
          cursor: "pointer",
        }}
      >
        ESC
      </button>
    </span>
  );
}

function Bars() {
  return (
    <div style={{ display: "flex", gap: 2, alignItems: "center", height: 16, flexShrink: 0 }}>
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
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
        padding: "6px 14px",
        borderRadius: 7,
        background: "linear-gradient(135deg, var(--accent), var(--accent-soft))",
        color: "var(--on-accent)",
        border: "none",
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.18em",
        textTransform: "uppercase",
        fontWeight: 700,
        boxShadow: hovered
          ? "0 0 22px var(--glow), 0 4px 8px rgba(0,0,0,.3)"
          : "0 0 14px var(--glow)",
        transform: hovered ? "translateY(-1px)" : "none",
        transition: "transform .15s, box-shadow .15s",
      }}
    >
      <span>Send</span>
      <svg
        width={12}
        height={12}
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
        color: "var(--fg-2)",
        border: "1px solid var(--line-hi)",
        borderRadius: 3,
        padding: "1px 4px",
        background: "color-mix(in srgb, var(--surface) 50%, transparent)",
      }}
    >
      {children}
    </span>
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
