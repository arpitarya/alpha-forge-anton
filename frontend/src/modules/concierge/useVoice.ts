"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getSRCtor, type WebkitSR } from "./webspeech.types";

const VOICE_ERRORS = {
  "not-allowed": "Microphone access denied. Allow it in your browser settings.",
  "permission-denied": "Microphone access denied. Allow it in your browser settings.",
  "audio-capture": "No microphone found. Plug one in and try again.",
  "no-speech": "No speech detected. Try speaking closer to the mic.",
  network: "Voice recognition needs a network connection.",
  "service-not-allowed": "Voice recognition is not allowed on this page.",
  aborted: "Voice input was cancelled.",
  "bad-grammar": "Voice grammar error.",
  "language-not-supported": "Language not supported.",
} as const;

interface VoiceState {
  supported: boolean;
  listening: boolean;
  transcript: string;
  interim: string;
  error: string | null;
}

interface Voice extends VoiceState {
  start: () => void;
  stop: () => void;
  speak: (text: string) => void;
  cancelSpeaking: () => void;
}

export function useVoice(onFinal?: (text: string) => void): Voice {
  const [state, setState] = useState<VoiceState>({
    supported: false,
    listening: false,
    transcript: "",
    interim: "",
    error: null,
  });
  // Holds the SR constructor (set once on mount, client-only)
  const SRCtorRef = useRef<{ new (): WebkitSR } | null>(null);
  // Holds the active recognition instance for the current session
  const recRef = useRef<WebkitSR | null>(null);
  const finalRef = useRef(onFinal);
  finalRef.current = onFinal;

  useEffect(() => {
    const SR = getSRCtor();
    SRCtorRef.current = SR;
    setState((s) => ({ ...s, supported: !!SR && "speechSynthesis" in window }));
    return () => {
      try {
        recRef.current?.abort();
      } catch {}
      recRef.current = null;
    };
  }, []);

  const start = useCallback(() => {
    const SR = SRCtorRef.current;
    if (!SR) return;

    // Always create a fresh instance — reusing a ended/aborted instance causes
    // Chrome to fire not-allowed on subsequent starts.
    try {
      recRef.current?.abort();
    } catch {}

    const rec = new SR();
    rec.continuous = false;
    rec.interimResults = true;
    rec.lang = "en-IN";
    rec.onresult = (e) => {
      let interim = "";
      let finalText = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interim += r[0].transcript;
      }
      setState((s) => ({ ...s, transcript: (s.transcript + finalText).trim(), interim }));
      if (finalText && finalRef.current) finalRef.current(finalText.trim());
    };
    rec.onerror = (e) => {
      const msg = VOICE_ERRORS[e.error as keyof typeof VOICE_ERRORS] ?? "Voice error. Try again.";
      setState((s) => ({ ...s, error: msg, listening: false }));
    };
    rec.onend = () => setState((s) => ({ ...s, listening: false, interim: "" }));
    recRef.current = rec;

    setState((s) => ({ ...s, listening: true, transcript: "", interim: "", error: null }));
    try {
      rec.start();
    } catch (e) {
      setState((s) => ({ ...s, listening: false, error: String(e) }));
    }
  }, []);

  const stop = useCallback(() => recRef.current?.stop(), []);

  const speak = useCallback((text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.05;
    u.lang = "en-IN";
    window.speechSynthesis.speak(u);
  }, []);

  const cancelSpeaking = useCallback(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
  }, []);

  return { ...state, start, stop, speak, cancelSpeaking };
}
