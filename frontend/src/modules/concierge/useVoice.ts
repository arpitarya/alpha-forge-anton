"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getSRCtor, type WebkitSR } from "./webspeech.types";

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
  const SR = getSRCtor();
  const [state, setState] = useState<VoiceState>({
    supported: !!SR && typeof window !== "undefined" && "speechSynthesis" in window,
    listening: false,
    transcript: "",
    interim: "",
    error: null,
  });
  const recRef = useRef<WebkitSR | null>(null);
  const finalRef = useRef(onFinal);
  finalRef.current = onFinal;

  useEffect(() => {
    if (!SR) return;
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
    rec.onerror = (e) =>
      setState((s) => ({ ...s, error: e.error || "voice error", listening: false }));
    rec.onend = () => setState((s) => ({ ...s, listening: false, interim: "" }));
    recRef.current = rec;
    return () => {
      try {
        rec.abort();
      } catch {}
      recRef.current = null;
    };
  }, [SR]);

  const start = useCallback(() => {
    if (!recRef.current) return;
    setState((s) => ({ ...s, listening: true, transcript: "", interim: "", error: null }));
    try {
      recRef.current.start();
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
