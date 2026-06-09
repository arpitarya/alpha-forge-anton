import type { ComponentType } from "react";

import { WHITELIST } from "./compose.registry";
import type { UINode } from "./compose.types";

interface Props {
  node: UINode;
  /** hookName → resolved data object, prepared by the host (keeps Rules of Hooks intact). */
  data?: Record<string, Record<string, unknown>>;
}

/**
 * Render a Fux-validated UISpec by mapping each node to a whitelisted primitive.
 * Unknown components render nothing — the whitelist is the client-side guardrail.
 * Declarative only: no `eval`, no dynamic import, no generated code is executed.
 */
export function DynamicRenderer({ node, data = {} }: Props) {
  if ("text" in node) {
    return <>{node.text}</>;
  }
  const Comp = WHITELIST[node.component] as ComponentType<Record<string, unknown>> | undefined;
  if (!Comp) {
    return null;
  }
  const bound = node.data ? (data[node.data] ?? {}) : {};
  const props = { ...bound, ...(node.props ?? {}) };
  const children = node.children?.map((child, i) => (
    // biome-ignore lint/suspicious/noArrayIndexKey: spec order is stable within a render
    <DynamicRenderer key={i} node={child} data={data} />
  ));
  return <Comp {...props}>{children}</Comp>;
}
