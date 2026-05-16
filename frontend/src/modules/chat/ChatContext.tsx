"use client";

import { usePathname } from "next/navigation";
import { createContext, type ReactNode, useContext, useRef, useState } from "react";
import { AlphaBar } from "./AlphaBar";
import { ChatRail } from "./ChatRail";
import type { ModelId } from "./chat.types";
import { useChatStream } from "./useChatStream";

interface ChatCtx {
  open: boolean;
  setOpen: (v: boolean) => void;
  submit: (q: string, model: ModelId) => void;
}

const Ctx = createContext<ChatCtx>({
  open: false,
  setOpen: () => {},
  submit: () => {},
});

export function ChatProvider({ children }: { children: ReactNode }) {
  const { turns, open, setOpen, submit, clear } = useChatStream();
  const footerModelRef = useRef<HTMLSpanElement>(null);
  const [activeModel, setActiveModel] = useState<ModelId>("auto");
  const pathname = usePathname();

  function handleSubmit(q: string, model: ModelId) {
    setActiveModel(model);
    submit(q, model);
  }

  // Don't render the bar/rail on login
  if (pathname === "/login") {
    return <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>{children}</Ctx.Provider>;
  }

  return (
    <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>
      {/*
        Outer column owns the full viewport height.
        AppShell (children) gets flex-1 + min-h-0 so it fills the space above the bar.
        AlphaBar is flex-none at the bottom — no overlap.
        ChatRail is absolute within this container so it overlays the content area.
      */}
      <div className="relative flex h-screen flex-col overflow-hidden">
        <div className="min-h-0 flex-1">{children}</div>
        <div className="flex-none px-3.5 pb-3.5 pt-2">
          <AlphaBar onSubmit={handleSubmit} footerModelRef={footerModelRef} />
        </div>
        <ChatRail
          open={open}
          turns={turns}
          modelId={activeModel}
          onClose={() => setOpen(false)}
          onClear={clear}
          onSeed={(q) => handleSubmit(q, activeModel)}
          footerModelRef={footerModelRef}
        />
      </div>
    </Ctx.Provider>
  );
}

export function useChat() {
  return useContext(Ctx);
}
