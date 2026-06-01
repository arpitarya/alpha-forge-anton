"use client";

import { notify } from "@alphaforge-anton/solar-ui";
import { useEffect, useState } from "react";
import { useVoice } from "./useVoice";

const VOICE_PROMPTS = [
  '"Orff, analyze my exposure to AI stocks"',
  '"Show banking drag this week"',
  '"Rebalance equity down 5% to target"',
  '"Screener: breakouts under ₹500"',
];

interface Props {
  onTranscript: (text: string) => void;
}

export function VoiceCenter({ onTranscript }: Props) {
  const [promptIdx, setPromptIdx] = useState(0);
  const voice = useVoice((finalText) => {
    if (finalText) onTranscript(finalText);
  });

  useEffect(() => {
    if (voice.listening) return;
    const id = setInterval(() => setPromptIdx((i) => (i + 1) % VOICE_PROMPTS.length), 3800);
    return () => clearInterval(id);
  }, [voice.listening]);

  useEffect(() => {
    if (!voice.error) return;
    notify.error({ title: "Voice input failed", message: voice.error });
  }, [voice.error]);

  const liveText = voice.transcribing
    ? "Transcribing…"
    : voice.listening
      ? voice.transcript || voice.interim || "Listening…"
      : VOICE_PROMPTS[promptIdx];

  return (
    <div style={{ display: "flex", minWidth: 0, flex: 1, alignItems: "center", gap: 14 }}>
      <MicToggle
        listening={voice.listening}
        supported={voice.supported}
        onClick={() => (voice.listening ? voice.stop() : voice.start())}
      />
      <div style={{ display: "flex", flexShrink: 0, alignItems: "center", gap: 8 }}>
        <span style={labelStyle}>
          {voice.transcribing ? "Transcribing…" : voice.listening ? "Listening…" : "Voice idle"}
        </span>
        <span style={subStyle}>· {voice.supported ? "WHISPER" : "UNAVAILABLE"}</span>
      </div>
      {voice.listening && <Waveform />}
      <span style={textStyle}>{liveText}</span>
    </div>
  );
}

function MicToggle({
  listening,
  supported,
  onClick,
}: {
  listening: boolean;
  supported: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={listening}
      aria-label={listening ? "Stop listening" : "Start listening"}
      disabled={!supported}
      onClick={onClick}
      style={{
        width: 28,
        height: 28,
        flexShrink: 0,
        display: "grid",
        placeItems: "center",
        borderRadius: "50%",
        border: `1px solid ${listening ? "var(--accent)" : "var(--line-hi)"}`,
        background: listening
          ? "color-mix(in srgb, var(--accent) 18%, transparent)"
          : "color-mix(in srgb, var(--surface-lo) 60%, transparent)",
        color: listening ? "var(--accent)" : "var(--fg-2)",
        boxShadow: listening ? "0 0 16px var(--glow)" : "none",
        cursor: supported ? "pointer" : "not-allowed",
        opacity: supported ? 1 : 0.45,
        transition: "all .18s",
      }}
    >
      <svg
        width={13}
        height={13}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
        role="img"
        aria-label="Microphone"
      >
        <title>Microphone</title>
        <rect x="9" y="3" width="6" height="12" rx="3" />
        <path d="M5 11a7 7 0 0 0 14 0" />
        <path d="M12 18v3M8 21h8" />
      </svg>
    </button>
  );
}

function Waveform() {
  return (
    <div style={{ display: "flex", flexShrink: 0, alignItems: "center", gap: 2, height: 16 }}>
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

const labelStyle = {
  color: "var(--accent)",
  fontSize: 12,
  fontStyle: "italic" as const,
  fontWeight: 500,
  letterSpacing: "0.04em",
};
const subStyle = {
  fontFamily: "Space Mono, monospace",
  fontSize: 9,
  letterSpacing: "0.22em",
  textTransform: "uppercase" as const,
  color: "var(--fg-3)",
};
const textStyle = {
  flex: 1,
  minWidth: 0,
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap" as const,
  fontSize: 12,
  color: "var(--fg-2)",
  fontStyle: "italic" as const,
};
