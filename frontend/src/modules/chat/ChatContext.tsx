"use client";

import { usePathname } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useRef, useState } from "react";
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

  const handleSubmit = useCallback(
    (q: string, model: ModelId) => {
      setActiveModel(model);
      submit(q, model);
    },
    [submit],
  );

  // Open the rail when chat mode is selected on the bar
  const handleChatModeOpen = useCallback(() => {
    setOpen(true);
  }, [setOpen]);

  if (pathname === "/login") {
    return <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>{children}</Ctx.Provider>;
  }

  return (
    <Ctx.Provider value={{ open, setOpen, submit: handleSubmit }}>
      <div className="relative flex h-screen flex-col overflow-hidden">
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{children}</div>
        <div className="flex-none px-3.5 pb-3.5 pt-2">
          {/* When rail is open, bar collapses to slim strip with no composer */}
          <AlphaBar
            onSubmit={handleSubmit}
            footerModelRef={footerModelRef}
            railOpen={open}
            onChatModeOpen={handleChatModeOpen}
          />
        </div>
        <ChatRail
          open={open}
          turns={turns}
          modelId={activeModel}
          onClose={() => setOpen(false)}
          onClear={clear}
          onSeed={(q) => handleSubmit(q, activeModel)}
          footerModelRef={footerModelRef}
          onModelChange={setActiveModel}
          query=""
        />
      </div>
    </Ctx.Provider>
  );
}

export function useChat() {
  return useContext(Ctx);
}
