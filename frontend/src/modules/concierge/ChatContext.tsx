"use client";

import { usePathname } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useRef, useState } from "react";
import { AlphaBar } from "./AlphaBar";
import { ChatRail } from "./ChatRail";
import { pickDefaultChoice } from "./concierge.defaults";
import type { ModelChoice } from "./concierge.types";
import { useChatStream } from "./useChatStream";

interface ChatCtx {
  open: boolean;
  setOpen: (v: boolean) => void;
  submit: (q: string, choice: ModelChoice) => void;
}

const Ctx = createContext<ChatCtx>({
  open: false,
  setOpen: () => {},
  submit: () => {},
});

const STORAGE_KEY = "af-model-choice";

function loadChoice(): ModelChoice {
  // A fresh session pins a derived default (see `pickDefaultChoice`) rather than
  // `auto`, so the model label stays stable while typing instead of re-routing
  // per keystroke. An explicit prior pick — including Auto — is always honoured.
  if (typeof window === "undefined") return pickDefaultChoice();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return pickDefaultChoice();
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && "provider" in parsed) return parsed as ModelChoice;
  } catch {}
  return pickDefaultChoice();
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const { turns, open, setOpen, submit, clear } = useChatStream();
  const footerModelRef = useRef<HTMLSpanElement>(null);
  const [choice, setChoice] = useState<ModelChoice>(loadChoice);
  const pathname = usePathname();

  const handleChoiceChange = useCallback((c: ModelChoice) => {
    setChoice(c);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(c));
    } catch {}
  }, []);

  const handleSubmit = useCallback((q: string, c: ModelChoice) => submit(q, c), [submit]);

  const handleChatModeOpen = useCallback(() => setOpen(true), [setOpen]);

  if (pathname === "/login") {
    return <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>{children}</Ctx.Provider>;
  }

  return (
    <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>
      <div className="relative flex h-screen flex-col overflow-hidden">
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{children}</div>
        <div className="flex-none px-3.5 pb-3.5 pt-2">
          <AlphaBar
            onSubmit={handleSubmit}
            choice={choice}
            onChoiceChange={handleChoiceChange}
            railOpen={open}
            onChatModeOpen={handleChatModeOpen}
            onClose={() => setOpen(false)}
          />
        </div>
        <ChatRail
          open={open}
          turns={turns}
          choice={choice}
          onClose={() => setOpen(false)}
          onClear={clear}
          onSeed={(q) => handleSubmit(q, choice)}
          footerModelRef={footerModelRef}
          onChoiceChange={handleChoiceChange}
        />
      </div>
    </Ctx.Provider>
  );
}

export function useChat() {
  return useContext(Ctx);
}
