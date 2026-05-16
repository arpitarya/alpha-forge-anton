"use client";

import { Button, Icon } from "@alphaforge/solar-orb-ui";
import type { SourceInfoDTO } from "./portfolio.types";
import { OTP_SLUGS } from "./sources.utils";
import type { useSourceRow } from "./useSourceRow.hook";

interface Props {
  src: SourceInfoDTO;
  r: ReturnType<typeof useSourceRow>;
}

export function SourceActions({ src, r }: Props) {
  const isOtp = OTP_SLUGS.has(src.slug);
  const showSync = (src.kind === "api" && !isOtp) || (isOtp && src.status === "ready");
  const showSendOtp = isOtp && src.status !== "ready";

  return (
    <div className="flex flex-wrap gap-2">
      {showSync && (
        <Button size="sm" variant="secondary" disabled={r.sync.isPending} onClick={r.handleSync}>
          <Icon name="sync" size="sm" className="mr-1" />
          {r.sync.isPending ? "Syncing…" : "Sync now"}
        </Button>
      )}
      {showSendOtp && (
        <Button
          size="sm"
          variant="secondary"
          disabled={r.startLogin.isPending}
          onClick={r.handleStartLogin}
        >
          <Icon name="key" size="sm" className="mr-1" />
          {r.startLogin.isPending ? "Sending OTP…" : "Send OTP"}
        </Button>
      )}
      {src.holdings_count > 0 && (
        <Button size="sm" variant="ghost" disabled={r.reset.isPending} onClick={r.handleReset}>
          Reset
        </Button>
      )}
    </div>
  );
}
