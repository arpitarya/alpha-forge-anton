// Minimal local typing for the Web Speech API surface we use.
// The browser DOM lib doesn't ship reliable types across all targets, so we
// declare just what we read.

export interface SRResult {
  readonly length: number;
  readonly isFinal: boolean;
  [index: number]: { readonly transcript: string };
}

export interface SRResultList {
  readonly length: number;
  [index: number]: SRResult;
}

export interface SREvent {
  readonly resultIndex: number;
  readonly results: SRResultList;
}

export interface SRErrorEvent {
  readonly error: string;
}

export interface WebkitSR extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((e: SREvent) => void) | null;
  onerror: ((e: SRErrorEvent) => void) | null;
  onend: (() => void) | null;
}

export function getSRCtor(): { new (): WebkitSR } | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: { new (): WebkitSR };
    webkitSpeechRecognition?: { new (): WebkitSR };
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}
