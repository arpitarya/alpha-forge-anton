"use client";

import { useEffect, useRef, useState } from "react";
import { ApprovalCard } from "./ApprovalCard";
import { ArtifactsPanel } from "./ArtifactsPanel";
import { CommandMenu } from "./CommandMenu";
import { CommandPalette } from "./CommandPalette";
import { downloadThread } from "./chat.export";
import { imagesFromClipboard, MAX_IMAGES } from "./chat.images";
import { matchCommands, resolveCommand, type SlashCommand } from "./concierge.commands";
import {
  type ChatTurn,
  type DeepSearchMode as DeepSearchModeType,
  formatChoiceLabel,
  type ModelChoice,
  type PendingAction,
  PROVIDERS,
  type ProviderId,
} from "./concierge.types";
import { DeepSearchMode } from "./DeepSearchMode";
import { FollowupChips } from "./FollowupChips";
import { GuardrailStrip } from "./GuardrailStrip";
import { HistoryPanel } from "./HistoryPanel";
import { ImageAttach } from "./ImageAttach";
import { MemoryPanel } from "./MemoryPanel";
import { ModelPicker } from "./ModelPicker";
import { ObjectivePanel } from "./ObjectivePanel";
import { ProposalDemo } from "./ProposalDemo";
import { SaveActionPlanButton } from "./SaveActionPlanButton";
import { SavePlanButton } from "./SavePlanButton";
import { SessionMeter } from "./SessionMeter";
import { SpecCard } from "./SpecCard";
import { ThinkingBlock } from "./ThinkingBlock";
import { ToolTrail } from "./ToolTrail";
import type { SessionTotals } from "./useChatStream";
import { useVoice } from "./useVoice";

type Panel = "none" | "artifacts" | "objective" | "memory" | "history";

interface Props {
  open: boolean;
  turns: ChatTurn[];
  choice: ModelChoice;
  totals: SessionTotals;
  sessionId: string;
  onResume: (id: string) => void;
  onClose: () => void;
  onClear: () => void;
  onSend: (q: string, images?: string[]) => void;
  /** Resend a closing turn carrying an approved deep-search result (forces mode=never). */
  onSendGrounded: (q: string, grounding: string) => void;
  onEdit: (id: string, q: string) => void;
  onStop: () => void;
  onChoiceChange: (c: ModelChoice) => void;
  footerModelRef: React.RefObject<HTMLSpanElement | null>;
  deepSearchMode: DeepSearchModeType;
  onDeepSearchModeChange: (m: DeepSearchModeType) => void;
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
  choice,
  totals,
  sessionId,
  onResume,
  onClose,
  onClear,
  onSend,
  onSendGrounded,
  onEdit,
  onStop,
  onChoiceChange,
  footerModelRef,
  deepSearchMode,
  onDeepSearchModeChange,
}: Props) {
  const [size, setSize] = useState<"md" | "lg">("md");
  const [inputValue, setInputValue] = useState("");
  const [lastSubmitted, setLastSubmitted] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [panel, setPanel] = useState<Panel>("none");
  const [demo, setDemo] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [cmdActive, setCmdActive] = useState(0);
  const [speakReplies, setSpeakReplies] = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const spokenRef = useRef<string | null>(null);
  const voice = useVoice();
  const thinking = turns.some((t) => t.loading);
  const done = !thinking && turns.length > 0 && turns[turns.length - 1]?.response != null;
  const turnCount = turns.length;
  const slashMatches = matchCommands(inputValue);

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

  // Escape closes (rail), Cmd/Ctrl+K opens the command palette
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((p) => !p);
        return;
      }
      if (e.key === "Escape" && open && !paletteOpen) onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose, paletteOpen]);

  // Speak the latest completed reply when readback is on (chat-app voice).
  useEffect(() => {
    if (!speakReplies) return;
    const last = turns[turns.length - 1];
    if (last && !last.loading && last.response && spokenRef.current !== last.id) {
      spokenRef.current = last.id;
      voice.speak(last.response);
    }
  }, [turns, speakReplies, voice]);

  function runCommand(c: SlashCommand) {
    setPaletteOpen(false);
    setInputValue("");
    if (c.body.kind === "send") {
      onSend(c.body.prompt);
      setLastSubmitted(c.body.prompt);
      return;
    }
    switch (c.body.action) {
      case "export":
        downloadThread(turns);
        break;
      case "memory":
        setPanel("memory");
        break;
      case "history":
        setPanel("history");
        break;
      case "artifacts":
        setPanel("artifacts");
        break;
      case "clear":
        onClear();
        break;
      case "stop":
        onStop();
        break;
      case "voice":
        setSpeakReplies((s) => !s);
        break;
      case "proposal":
        setPanel("none");
        setDemo(true);
        break;
    }
  }

  function handleSubmit() {
    const q = inputValue.trim();
    const cmd = resolveCommand(q);
    if (cmd) {
      runCommand(cmd);
      if (textareaRef.current) textareaRef.current.style.height = "auto";
      return;
    }
    if (!q && !images.length) return;
    onSend(q, images);
    setLastSubmitted(q);
    setInputValue("");
    setImages([]);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (slashMatches.length && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
      e.preventDefault();
      setCmdActive((a) =>
        e.key === "ArrowDown" ? Math.min(a + 1, slashMatches.length - 1) : Math.max(a - 1, 0),
      );
      return;
    }
    if (slashMatches.length && (e.key === "Tab" || (e.key === "Enter" && !e.shiftKey))) {
      e.preventDefault();
      const picked = slashMatches[Math.min(cmdActive, slashMatches.length - 1)];
      if (picked) runCommand(picked);
      return;
    }
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  async function handlePaste(e: React.ClipboardEvent) {
    const found = await imagesFromClipboard(e.clipboardData.items);
    if (found.length) {
      e.preventDefault();
      setImages((prev) => [...prev, ...found].slice(0, MAX_IMAGES));
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
          flexDirection: "row",
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

        {/* ── Left nav sidebar ── */}
        <nav
          aria-label="Alpha modes"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
            width: 58,
            flexShrink: 0,
            padding: "16px 0",
            borderRight: "1px solid var(--line)",
            background: "linear-gradient(180deg, #0e0e0e, #0a0a0a)",
            borderRadius: "18px 0 0 18px",
          }}
        >
          <span
            style={{
              width: 30,
              height: 30,
              borderRadius: "50%",
              flexShrink: 0,
              marginBottom: 8,
              background:
                "radial-gradient(circle at 36% 32%, #fff, var(--accent-soft) 20%, var(--accent) 58%, transparent)",
              boxShadow: "0 0 16px var(--glow)",
              animation: "breathe 4s ease-in-out infinite",
              display: "block",
            }}
          />
          <NavBtn active={panel === "none"} title="Chat" onClick={() => setPanel("none")}>
            <ChatNavIcon />
          </NavBtn>
          <NavBtn
            active={panel === "artifacts"}
            title="Artifacts"
            onClick={() => setPanel((p) => (p === "artifacts" ? "none" : "artifacts"))}
          >
            <SparkIcon />
          </NavBtn>
          <NavBtn
            active={panel === "objective"}
            title="Objective"
            onClick={() => setPanel((p) => (p === "objective" ? "none" : "objective"))}
          >
            <TargetIcon />
          </NavBtn>
          <NavBtn
            active={panel === "memory"}
            title="Memory"
            onClick={() => setPanel((p) => (p === "memory" ? "none" : "memory"))}
          >
            <BrainIcon />
          </NavBtn>
          <NavBtn
            active={panel === "history"}
            title="History"
            onClick={() => setPanel((p) => (p === "history" ? "none" : "history"))}
          >
            <HistoryIcon />
          </NavBtn>
          <NavBtn
            active={speakReplies}
            title={speakReplies ? "Voice readback on" : "Voice readback off"}
            onClick={() => {
              setSpeakReplies((s) => !s);
              voice.cancelSpeaking();
            }}
          >
            <MicNavIcon />
          </NavBtn>
          <span style={{ flex: 1 }} />
          <NavBtn title="Commands (⌘K)" onClick={() => setPaletteOpen(true)}>
            <SearchIcon />
          </NavBtn>
        </nav>

        {/* ── Main content column ── */}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            display: "flex",
            flexDirection: "column",
            borderRadius: "0 18px 18px 0",
            overflow: "hidden",
          }}
        >
          {/* ── Header ── */}
          <header
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "14px 18px",
              borderBottom: "1px solid var(--line)",
              flexShrink: 0,
              background: "color-mix(in srgb, var(--surface) 60%, transparent)",
              borderRadius: "0 18px 0 0",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                minWidth: 0,
                flex: "0 1 auto",
              }}
            >
              <div style={{ minWidth: 0 }}>
                <div
                  style={{
                    fontSize: 15.5,
                    fontWeight: 500,
                    letterSpacing: "-0.005em",
                    lineHeight: 1.1,
                    color: "var(--fg)",
                  }}
                >
                  Conversation
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
                      background: thinking
                        ? "var(--accent)"
                        : done
                          ? "var(--green)"
                          : "var(--fg-4)",
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
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                fontFamily: "Space Mono, monospace",
                fontSize: 8.5,
                letterSpacing: "0.16em",
                textTransform: "uppercase",
                color: "var(--green)",
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "var(--green)",
                  boxShadow: "0 0 6px rgba(55,209,122,.6)",
                  display: "inline-block",
                }}
              />
              online
            </span>
            <div
              style={{
                marginLeft: "auto",
                display: "flex",
                alignItems: "center",
                gap: 12,
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 7,
                  fontFamily: "Space Mono, monospace",
                  fontSize: 10,
                  color: "var(--fg-2)",
                  whiteSpace: "nowrap",
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: "var(--accent)",
                    boxShadow: "0 0 8px var(--glow)",
                    display: "inline-block",
                  }}
                />
                <span ref={footerModelRef}>Auto → Claude Sonnet 4.6</span>
              </span>
              <SessionMeter totals={totals} />
              <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                {thinking && (
                  <CrBtn title="Stop generating" onClick={onStop} danger>
                    ◼
                  </CrBtn>
                )}
                <CrBtn title="Export thread" onClick={() => downloadThread(turns)}>
                  ⤓
                </CrBtn>
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
            </div>
          </header>

          {/* ── Thread / side panel ── */}
          {panel === "objective" ? (
            <div style={{ flex: 1, minHeight: 0 }}>
              <ObjectivePanel
                onEdit={(q) => {
                  setPanel("none");
                  onSend(q);
                }}
                onClose={() => setPanel("none")}
              />
            </div>
          ) : panel === "memory" ? (
            <div style={{ flex: 1, minHeight: 0 }}>
              <MemoryPanel onClose={() => setPanel("none")} />
            </div>
          ) : panel === "history" ? (
            <div style={{ flex: 1, minHeight: 0 }}>
              <HistoryPanel
                activeId={sessionId}
                onResume={(id) => {
                  onResume(id);
                  setPanel("none");
                }}
                onClose={() => setPanel("none")}
              />
            </div>
          ) : panel === "artifacts" ? (
            <div style={{ flex: 1, minHeight: 0 }}>
              <ArtifactsPanel turns={turns} onClose={() => setPanel("none")} />
            </div>
          ) : (
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
              {/* Pinned READ-ONLY guardrail — the mandate every answer is measured against. */}
              <GuardrailStrip />
              {turns.length === 0 && !demo ? (
                <EmptyState onSeed={(q) => onSend(q)} onProposal={() => setDemo(true)} />
              ) : (
                turns.map((turn) => (
                  <TurnPair
                    key={turn.id}
                    turn={turn}
                    thinking={thinking}
                    onEdit={onEdit}
                    onPickFollowup={(q) => onSend(q)}
                    onSendGrounded={onSendGrounded}
                  />
                ))
              )}
              {demo && <ProposalDemo />}
            </div>
          )}

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
                position: "relative",
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
              <CommandMenu
                commands={slashMatches}
                active={Math.min(cmdActive, Math.max(slashMatches.length - 1, 0))}
                onPick={runCommand}
              />
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
                    setCmdActive(0);
                    autoGrow(e.target);
                  }}
                  onKeyDown={handleKeyDown}
                  onPaste={(e) => void handlePaste(e)}
                  placeholder="Ask Alpha — “/” for commands, ⌘K palette, paste an image…"
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
                <div
                  style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0, flex: 1 }}
                >
                  <ImageAttach images={images} onChange={setImages} />
                  <DeepSearchMode value={deepSearchMode} onChange={onDeepSearchModeChange} />
                  <ModelPicker
                    value={choice}
                    query={inputValue || lastSubmitted}
                    onChange={onChoiceChange}
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
                  {thinking ? (
                    <StopButton onClick={onStop} />
                  ) : (
                    <SendButton onClick={handleSubmit} />
                  )}
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
                letterSpacing: "0.14em",
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
                <span>streaming</span>
              </span>
              <span style={{ opacity: 0.6 }}>
                <Kbd>↵</Kbd> send · <Kbd>/</Kbd> commands · <Kbd>⌘K</Kbd> palette · Esc close
              </span>
            </div>
          </div>
        </div>
        {/* /main content column */}
      </aside>

      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onPick={runCommand}
      />
    </>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────

function MiniBtn({
  label,
  onClick,
  primary,
}: {
  label: string;
  onClick: () => void;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        padding: "5px 12px",
        borderRadius: 6,
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        border: primary ? "none" : "1px solid var(--line-hi)",
        color: primary ? "var(--on-accent)" : "var(--fg-2)",
        background: primary ? "var(--accent)" : "transparent",
      }}
    >
      {label}
    </button>
  );
}

function StopButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      title="Stop generating"
      aria-label="Stop generating"
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        padding: "5px 12px",
        borderRadius: 6,
        background: "transparent",
        color: "var(--fg-2)",
        border: "1px solid var(--line-hi)",
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
      }}
    >
      <span style={{ fontSize: 9 }}>◼</span>
      <span>Stop</span>
    </button>
  );
}

function NavBtn({
  active,
  title,
  onClick,
  children,
}: {
  active?: boolean;
  title: string;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const [hov, setHov] = useState(false);
  return (
    <button
      type="button"
      title={title}
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width: 38,
        height: 38,
        display: "grid",
        placeItems: "center",
        borderRadius: 9,
        color: active ? "var(--on-accent)" : hov ? "var(--fg-2)" : "var(--fg-3)",
        background: active
          ? "var(--accent)"
          : hov
            ? "color-mix(in srgb, var(--accent) 8%, transparent)"
            : "transparent",
        border: "1px solid transparent",
        boxShadow: active ? "0 0 16px var(--glow)" : "none",
        transition: "all .18s",
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}

function ChatNavIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 5h16v11H8l-4 4z" />
      <path d="M8 10h8M8 13h5" />
    </svg>
  );
}
function MicNavIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
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
function SparkIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" />
    </svg>
  );
}
function BrainIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M9 3a3 3 0 0 0-3 3 3 3 0 0 0-1 5.8A3 3 0 0 0 7 17a3 3 0 0 0 5 1 3 3 0 0 0 5-1 3 3 0 0 0 2-5.2A3 3 0 0 0 18 6a3 3 0 0 0-3-3 3 3 0 0 0-3 1.5A3 3 0 0 0 9 3z" />
      <path d="M12 5v13" />
    </svg>
  );
}
function TargetIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1" />
    </svg>
  );
}
function HistoryIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
      <path d="M3 4v4h4M12 8v4l3 2" />
    </svg>
  );
}
function SearchIcon() {
  return (
    <svg
      width={17}
      height={17}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
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

function EmptyState({
  onSeed,
  onProposal,
}: {
  onSeed: (q: string) => void;
  onProposal: () => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        padding: "28px 16px 16px",
        gap: 8,
        color: "var(--fg-3)",
      }}
    >
      <div
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9.5,
          letterSpacing: "0.32em",
          textTransform: "uppercase",
          color: "var(--accent)",
        }}
      >
        Alpha Forge · Online
      </div>
      <div
        style={{
          fontSize: 22,
          fontWeight: 500,
          letterSpacing: "-0.015em",
          color: "var(--fg)",
          lineHeight: 1.2,
          marginTop: 4,
        }}
      >
        Hi. Ready when you are.
      </div>
      <div
        style={{
          fontSize: 13,
          color: "var(--fg-3)",
          lineHeight: 1.55,
          fontFamily: "Space Grotesk, sans-serif",
          marginBottom: 8,
        }}
      >
        Ask anything about your portfolio, scan markets, simulate a rebalance, or just brainstorm a
        thesis.
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 7, width: "100%" }}>
        {SEEDS.map((s) => (
          <FuChip key={s.q} seed={s} onSeed={onSeed} />
        ))}
        <button
          type="button"
          onClick={onProposal}
          style={{
            marginTop: 4,
            padding: "10px 14px",
            borderRadius: 10,
            textAlign: "left",
            fontFamily: "Space Mono, monospace",
            fontSize: 10,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color: "var(--accent)",
            background: "color-mix(in srgb, var(--accent) 6%, transparent)",
            border: "1px solid color-mix(in srgb, var(--accent) 35%, var(--line))",
            cursor: "pointer",
          }}
        >
          ◆ Show the RBI proposal — downside-first cone + approval (demo)
        </button>
      </div>
    </div>
  );
}

function FuChip({ seed, onSeed }: { seed: (typeof SEEDS)[0]; onSeed: (q: string) => void }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      type="button"
      onClick={() => onSeed(seed.q)}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        display: "grid",
        gridTemplateColumns: "34px 1fr auto",
        gap: 12,
        alignItems: "center",
        padding: "11px 14px",
        borderRadius: 10,
        textAlign: "left",
        fontFamily: "Space Grotesk, sans-serif",
        background: hov
          ? "color-mix(in srgb, var(--accent) 6%, var(--surface-lo))"
          : "color-mix(in srgb, var(--surface-lo) 45%, transparent)",
        border: `1px solid ${hov ? "color-mix(in srgb, var(--accent) 50%, var(--line-hi))" : "var(--line)"}`,
        cursor: "pointer",
        transition: "all .18s ease",
      }}
    >
      <span
        style={{
          width: 34,
          height: 34,
          borderRadius: 8,
          display: "grid",
          placeItems: "center",
          background: hov
            ? "color-mix(in srgb, var(--accent) 22%, transparent)"
            : "color-mix(in srgb, var(--accent) 12%, transparent)",
          border: `1px solid ${hov ? "color-mix(in srgb, var(--accent) 55%, transparent)" : "color-mix(in srgb, var(--accent) 30%, transparent)"}`,
          color: "var(--accent)",
          flexShrink: 0,
          transition: "all .18s",
        }}
      >
        {seed.icon}
      </span>
      <span style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
        <span
          style={{
            fontSize: 13,
            fontWeight: 500,
            color: hov ? "var(--fg)" : "var(--fg-2)",
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
          opacity: hov ? 1 : 0.35,
          transform: hov ? "translateX(2px)" : "translateX(0)",
          transition: "all .18s",
          flexShrink: 0,
        }}
      >
        →
      </span>
    </button>
  );
}

function resolveResponderLabel(turn: ChatTurn): string {
  if (turn.provider && turn.model) {
    const providerMeta = PROVIDERS[turn.provider as ProviderId];
    const providerName = providerMeta?.name ?? turn.provider;
    const modelName = providerMeta?.models.find((m) => m.id === turn.model)?.name ?? turn.model;
    return `${providerName} · ${modelName}`;
  }
  return formatChoiceLabel(turn.active);
}

/** POST a confirm card's apply target; returns the parsed JSON ({} on any failure —
 * fail-open, mirroring the backend's deep-search degrade-to-free-sources contract). */
async function postApply(
  apply: NonNullable<PendingAction["apply"]>,
): Promise<Record<string, unknown>> {
  const tok = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
  try {
    const res = await fetch(apply.path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(tok ? { Authorization: `Bearer ${tok}` } : {}),
      },
      body: JSON.stringify(apply.body),
    });
    return res.ok ? await res.json() : {};
  } catch {
    return {};
  }
}

function TurnPair({
  turn,
  thinking,
  onEdit,
  onPickFollowup,
  onSendGrounded,
}: {
  turn: ChatTurn;
  thinking: boolean;
  onEdit: (id: string, q: string) => void;
  onPickFollowup: (q: string) => void;
  onSendGrounded: (q: string, grounding: string) => void;
}) {
  const modelName = formatChoiceLabel(turn.active);
  const responderLabel = resolveResponderLabel(turn);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(turn.query);

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
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontFamily: "Space Mono, monospace",
            fontSize: 9,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--fg-4)",
          }}
        >
          <span>
            YOU · <b style={{ color: "var(--fg-3)", fontWeight: 400 }}>{timeStr}</b>
          </span>
          {!editing && (
            <button
              type="button"
              title="Edit & branch"
              onClick={() => {
                setDraft(turn.query);
                setEditing(true);
              }}
              style={{
                border: "none",
                background: "transparent",
                color: "var(--fg-4)",
                cursor: "pointer",
                fontSize: 11,
                padding: 0,
              }}
            >
              ✎
            </button>
          )}
        </div>
        {turn.images && turn.images.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
            {turn.images.map((src) => (
              // biome-ignore lint/performance/noImgElement: local data URL preview, not remote
              <img
                key={src.slice(-32)}
                src={src}
                alt="attachment"
                style={{ width: 64, height: 64, borderRadius: 8, objectFit: "cover" }}
              />
            ))}
          </div>
        )}
        {editing ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 6, width: "100%" }}>
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              rows={2}
              style={{
                width: "100%",
                resize: "none",
                padding: "10px 14px",
                borderRadius: 12,
                border: "1px solid color-mix(in srgb, var(--accent) 40%, var(--line-hi))",
                background: "var(--surface-lo)",
                color: "var(--fg)",
                fontFamily: "Space Grotesk, sans-serif",
                fontSize: 13.5,
                outline: "none",
              }}
            />
            <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
              <MiniBtn label="Cancel" onClick={() => setEditing(false)} />
              <MiniBtn
                primary
                label="Send"
                onClick={() => {
                  const q = draft.trim();
                  setEditing(false);
                  if (q && q !== turn.query) onEdit(turn.id, q);
                }}
              />
            </div>
          </div>
        ) : (
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
        )}
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
            <span style={{ color: "var(--accent)", fontWeight: 700 }}>ORFF</span>
            <span>·</span>
            <span style={{ marginLeft: "auto", textTransform: "none", letterSpacing: "0.06em" }}>
              {turn.loading
                ? `thinking · ${modelName}`
                : `${turn.tokens ?? 0} tok · ${responderLabel}${turn.elapsed != null ? ` · ${turn.elapsed.toFixed(1)}s` : ""}`}
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
            {turn.tools && turn.tools.length > 0 && <ToolTrail steps={turn.tools} />}
            {turn.thinking ? (
              <ThinkingBlock text={turn.thinking} streaming={turn.loading && !turn.response} />
            ) : null}
            {turn.loading && !turn.response && !turn.thinking ? (
              <TypingIndicator />
            ) : turn.error ? (
              <span style={{ color: "var(--red)", fontSize: 12 }}>Error: {turn.error}</span>
            ) : (
              <>
                <ResponseBody text={turn.response ?? ""} />
                {turn.spec && <SpecCard spec={turn.spec} />}
                {turn.confirm && (
                  <ApprovalCard
                    action={turn.confirm}
                    onApprove={(a: PendingAction) => {
                      // Deep-search is the one card that closes in place: await the run,
                      // then resend with its grounding (mode forced to never) so Orff
                      // answers instead of re-arming the card. Every other card keeps the
                      // fire-and-forget POST + reprompt (it re-reads its elgar write next turn).
                      if (a.id === "deep-search" && a.apply) {
                        void postApply(a.apply).then((data) =>
                          onSendGrounded(
                            `Reconcile your answer using these deep-search results for: ${a.summary}`,
                            String(data?.grounding ?? ""),
                          ),
                        );
                        return;
                      }
                      if (a.apply) void postApply(a.apply);
                      onPickFollowup(`Yes — proceed with: ${a.action}. ${a.summary}`);
                    }}
                    onDismiss={() => {}}
                  />
                )}
                {!turn.loading && turn.followups && turn.followups.length > 0 && (
                  <FollowupChips chips={turn.followups} onPick={onPickFollowup} />
                )}
                {!turn.loading && turn.response && (
                  <SavePlanButton title={turn.query} content={turn.response} />
                )}
                {!turn.loading && turn.spec && /review/i.test(turn.query) && (
                  <SaveActionPlanButton />
                )}
              </>
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

function MdTable({ lines }: { lines: string[] }) {
  const parseRow = (line: string) =>
    line
      .split("|")
      .slice(1, -1)
      .map((c) => c.trim());
  const isSeparator = (line: string) => /^[\s|:=-]+$/.test(line);

  const [headerLine, ...rest] = lines;
  if (!headerLine) return null;
  const headers = parseRow(headerLine);
  const bodyLines = rest.filter((l) => !isSeparator(l));

  function severityStyle(cell: string): React.CSSProperties {
    const v = cell.toLowerCase();
    if (v === "high") return { color: "var(--red)", fontWeight: 600 };
    if (v === "medium") return { color: "#f59e0b", fontWeight: 600 };
    if (v === "low") return { color: "var(--green)", fontWeight: 600 };
    return {};
  }

  return (
    <div className="rb-table-wrap">
      <table className="rb-table">
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyLines.map((line) => (
            <tr key={line.slice(0, 40)}>
              {parseRow(line).map((cell, j) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: table cells have no stable id
                <td key={j} style={severityStyle(cell)}>
                  <InlineTokens text={cell} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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

    if (raw.trim().startsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      nodes.push(<MdTable key={`tbl-${i}`} lines={tableLines} />);
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
