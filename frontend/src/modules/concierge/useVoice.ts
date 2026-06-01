"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface VoiceState {
  supported: boolean;
  listening: boolean;
  transcribing: boolean;
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

function pickMimeType(): string {
  if (typeof MediaRecorder === "undefined") return "";
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"];
  return candidates.find((t) => MediaRecorder.isTypeSupported(t)) ?? "";
}

export function useVoice(onFinal?: (text: string) => void): Voice {
  const [state, setState] = useState<VoiceState>({
    supported: false,
    listening: false,
    transcribing: false,
    transcript: "",
    interim: "",
    error: null,
  });
  const recRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const finalRef = useRef(onFinal);
  finalRef.current = onFinal;

  useEffect(() => {
    const supported =
      typeof window !== "undefined" &&
      !!navigator.mediaDevices?.getUserMedia &&
      typeof MediaRecorder !== "undefined";
    setState((s) => ({ ...s, supported }));
    return () => {
      try {
        if (recRef.current?.state === "recording") recRef.current.stop();
      } catch {}
      streamRef.current?.getTracks().forEach((t) => {
        t.stop();
      });
      streamRef.current = null;
      recRef.current = null;
    };
  }, []);

  const teardown = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => {
      t.stop();
    });
    streamRef.current = null;
    recRef.current = null;
  }, []);

  const transcribe = useCallback(async (blob: Blob) => {
    setState((s) => ({ ...s, transcribing: true }));
    try {
      const form = new FormData();
      const ext = blob.type.includes("mp4") ? "m4a" : "webm";
      form.append("file", blob, `voice.${ext}`);
      const token = localStorage.getItem("af_token");
      const res = await fetch("/api/v1/concierge/stt", {
        method: "POST",
        body: form,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`STT ${res.status}: ${detail.slice(0, 120)}`);
      }
      const { transcript } = (await res.json()) as { transcript: string };
      const clean = (transcript ?? "").trim();
      setState((s) => ({ ...s, transcript: clean, transcribing: false, interim: "" }));
      if (clean && finalRef.current) finalRef.current(clean);
    } catch (e) {
      setState((s) => ({
        ...s,
        transcribing: false,
        error: e instanceof Error ? e.message : "Transcription failed",
      }));
    }
  }, []);

  const start = useCallback(async () => {
    if (recRef.current?.state === "recording") return;
    setState((s) => ({ ...s, transcript: "", interim: "", error: null }));

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      const name = e instanceof Error ? e.name : "Error";
      const msg =
        name === "NotAllowedError"
          ? "Microphone access denied. Allow it in your browser settings."
          : name === "NotFoundError"
            ? "No microphone found. Plug one in and try again."
            : `Microphone error: ${name}`;
      setState((s) => ({ ...s, error: msg, listening: false }));
      return;
    }

    streamRef.current = stream;
    const mime = pickMimeType();
    const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
    chunksRef.current = [];

    rec.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
    };
    rec.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mime || "audio/webm" });
      chunksRef.current = [];
      teardown();
      setState((s) => ({ ...s, listening: false }));
      if (blob.size > 0) void transcribe(blob);
    };
    rec.onerror = (e) => {
      const err = (e as unknown as { error?: { name?: string } }).error;
      setState((s) => ({
        ...s,
        error: `Recorder error: ${err?.name ?? "unknown"}`,
        listening: false,
      }));
      teardown();
    };

    recRef.current = rec;
    rec.start();
    setState((s) => ({ ...s, listening: true }));
  }, [teardown, transcribe]);

  const stop = useCallback(() => {
    const rec = recRef.current;
    if (rec && rec.state === "recording") rec.stop();
  }, []);

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
