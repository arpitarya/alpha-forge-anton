/** A declarative UI tree Orff generates and Fux validates (§18.3). Never code. */
export type UINode =
  | { text: string }
  | {
      component: string;
      props?: Record<string, unknown>;
      data?: string;
      children?: UINode[];
    };

export interface ComposeResponse {
  spec: UINode | null;
  valid: boolean;
  errors: string[];
  provider?: string;
  model?: string;
  attempts: number;
}
