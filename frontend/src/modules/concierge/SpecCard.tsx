"use client";

import type { UINode } from "./compose.types";
import { SpecHost } from "./SpecHost";

interface Props {
  spec: UINode;
}

/**
 * Inline frame for a generated UI inside a chat turn — labelled so generated
 * surfaces are always distinguishable from hand-built ones.
 */
export function SpecCard({ spec }: Props) {
  return (
    <div
      style={{
        marginTop: 12,
        padding: "12px 14px",
        borderRadius: 10,
        border: "1px solid color-mix(in srgb, var(--accent) 30%, var(--line))",
        background: "color-mix(in srgb, var(--surface) 80%, transparent)",
      }}
    >
      <div
        style={{
          marginBottom: 10,
          fontFamily: "Space Mono, monospace",
          fontSize: 8,
          letterSpacing: "0.22em",
          textTransform: "uppercase",
          color: "var(--accent)",
        }}
      >
        composed ui · fux-validated
      </div>
      <SpecHost spec={spec} />
    </div>
  );
}
