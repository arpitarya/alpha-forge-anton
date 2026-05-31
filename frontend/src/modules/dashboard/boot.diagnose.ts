import { type NotificationAction, notify } from "@alphaforge-anton/solar-ui";

export interface Failure {
  slug: string;
  reason?: string;
  detail: string;
}

export interface Diagnosis {
  /** Headline for the notification — what went wrong, in plain English. */
  title: string;
  /** Single explanatory line shown under the title. Includes the affected brokers. */
  message: string;
  /** Up to 2 actions the user can take (Reload is always appended as a fallback). */
  actions: NotificationAction[];
}

interface Pattern {
  match: (reason: string) => boolean;
  build: (
    failures: Failure[],
    total: number,
  ) => Omit<Diagnosis, "actions"> & { actions?: NotificationAction[] };
}

// Order matters — first match wins. Specific patterns before general ones.
const PATTERNS: Pattern[] = [
  {
    match: (r) => /vault is locked|afbach.*lock|cannot load/i.test(r),
    build: (fs) => ({
      title: "Vault is locked",
      message: `Broker credentials can't load. Run "afbach unlock" in your terminal, then reload. Affects: ${slugList(fs)}.`,
      actions: [
        {
          label: "Copy unlock command",
          variant: "line",
          onClick: () => copyAndConfirm("afbach unlock"),
        },
      ],
    }),
  },
  {
    match: (r) => /timeout|timed out/i.test(r),
    build: (fs) => ({
      title: `${fs.length} broker${plural(fs)} timed out`,
      message: `Upstream broker(s) too slow to respond: ${slugList(fs)}. Often transient.`,
    }),
  },
  {
    match: (r) => /401|unauthor|expired|invalid.*token|session/i.test(r),
    build: (fs) => ({
      title: "Broker session expired",
      message: `Re-authenticate the broker login: ${slugList(fs)}.`,
      actions: [
        { label: "Open Sources", variant: "line", onClick: () => goto("/portfolio?panel=sources") },
      ],
    }),
  },
  {
    match: (r) => /network|ECONN|getaddrinfo|DNS|unreachable/i.test(r),
    build: (fs) => ({
      title: "Can't reach broker servers",
      message: `Network or upstream outage. Affects: ${slugList(fs)}.`,
    }),
  },
  {
    match: (r) => /rate.?limit|429|too many/i.test(r),
    build: (fs) => ({
      title: "Broker rate-limited",
      message: `${slugList(fs)} hit a request cap. Backend will retry on the next TTL tick.`,
    }),
  },
];

export function diagnose(failures: Failure[], total: number): Diagnosis {
  const grouped = groupByReason(failures);
  // Single dominant reason — surface it with a tailored fix
  if (grouped.length === 1) {
    const [reason, group] = grouped[0];
    const pattern = PATTERNS.find((p) => reason && p.match(reason));
    if (pattern) {
      const built = pattern.build(group, total);
      return {
        title: built.title,
        message: built.message,
        actions: [...(built.actions ?? []), reloadAction()],
      };
    }
  }
  // Heterogeneous failures — show the count and the most common reason if any
  const topReason = grouped[0]?.[0];
  return {
    title: `${failures.length} of ${total} broker${total === 1 ? "" : "s"} failed`,
    message: topReason
      ? `Most common reason: "${truncate(topReason, 80)}". Affected: ${slugList(failures)}.`
      : `Affected: ${slugList(failures)}.`,
    actions: [reloadAction()],
  };
}

function groupByReason(failures: Failure[]): Array<[string, Failure[]]> {
  const map = new Map<string, Failure[]>();
  for (const f of failures) {
    const key = (f.reason || f.detail || "unknown").trim();
    const arr = map.get(key) ?? [];
    arr.push(f);
    map.set(key, arr);
  }
  return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
}

const slugList = (fs: Failure[]) => fs.map((f) => f.slug).join(", ");
const plural = (fs: Failure[]) => (fs.length === 1 ? "" : "s");
const truncate = (s: string, n: number) => (s.length <= n ? s : `${s.slice(0, n - 1)}…`);

const reloadAction = (): NotificationAction => ({
  label: "Reload",
  variant: "solid",
  onClick: () => location.reload(),
});

function goto(href: string): void {
  if (typeof window !== "undefined") window.location.assign(href);
}

function copyAndConfirm(text: string): void {
  if (typeof navigator === "undefined" || !navigator.clipboard) return;
  navigator.clipboard
    .writeText(text)
    .then(() => notify.ok({ title: "Copied", pill: "clipboard", message: `"${text}"`, ttl: 2500 }))
    .catch(() =>
      notify.warn({
        title: "Couldn't copy",
        message: `Run "${text}" manually in your terminal.`,
      }),
    );
}
