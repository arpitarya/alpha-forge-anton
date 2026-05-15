import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface VoiceDockProps {
  mic?: ReactNode;
  /** Status block — typically <Waveform/> + transcript text. */
  center?: ReactNode;
  /** Right-side action — typically a <Button variant="deploy" />. */
  cta?: ReactNode;
  className?: string;
}

/**
 * Hi-Fi `.voice` footer — surface card with a left accent stripe wrapping
 * mic + waveform + CTA.
 *
 * Layout uses a plain flex row (mic / center auto-grows / cta) instead of
 * `grid-cols-[auto_1fr_auto]` because the grid arbitrary-value form was
 * unreliable in some Tailwind v4 configurations and silently fell back to
 * vertical stacking, which broke the dock on the terminal screen.
 */
export function VoiceDock({ mic, center, cta, className }: VoiceDockProps) {
  return (
    <footer
      data-af-voice
      className={twMerge(
        clsx(
          "af-voice group/voice relative flex flex-none items-center gap-4 min-h-[36px]",
          "rounded-[8px] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_82%,transparent)]",
          "px-3.5 py-1.5 [backdrop-filter:blur(18px)] [-webkit-backdrop-filter:blur(18px)]",
          "before:absolute before:left-0 before:top-0 before:h-full before:w-0.5",
          "before:bg-[linear-gradient(180deg,transparent,var(--accent),transparent)]",
          "before:opacity-50 before:content-['']",
          className,
        ),
      )}
    >
      {mic && <div className="flex flex-none items-center">{mic}</div>}
      <div className="flex min-w-0 flex-1 items-center gap-3.5">{center}</div>
      {cta && <div className="flex flex-none items-center">{cta}</div>}
    </footer>
  );
}
