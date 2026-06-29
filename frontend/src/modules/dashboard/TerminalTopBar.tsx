"use client";

import { Kbd, LiveDot, Logo, TopBar, type TopBarNavItem } from "@alphaforge-anton/solar-ui";
import { clsx } from "clsx";
import { LogOut } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { useAuthStore } from "@/modules/auth/useAuthStore";

const NAV_ITEMS: Array<{ id: string; label: string; href: string }> = [
  { id: "terminal", label: "Terminal", href: "/" },
  { id: "portfolio", label: "Portfolio", href: "/portfolio" },
  { id: "flow", label: "Flow", href: "/flow" },
  { id: "goals", label: "Goals", href: "/goals" },
  { id: "decisions", label: "Decisions", href: "/decisions" },
];

function isActive(pathname: string | null, href: string): boolean {
  if (!pathname) return href === "/";
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TerminalTopBar() {
  const router = useRouter();
  const pathname = usePathname();
  const prefsActive = isActive(pathname, "/preferences");
  const logout = useAuthStore((s) => s.logout);
  const [loggingOut, setLoggingOut] = useState(false);

  const nav: TopBarNavItem[] = NAV_ITEMS.map((n) => ({
    id: n.id,
    label: n.label,
    active: isActive(pathname, n.href),
    onClick: () => router.push(n.href),
  }));

  async function handleLogout() {
    if (loggingOut) return;
    setLoggingOut(true);
    await logout();
    router.replace("/login");
  }

  return (
    <TopBar
      brand={<Logo variant="lockup" size="xs" />}
      nav={nav}
      right={
        <>
          <LiveDot label="LIVE · NSE" />
          <Kbd>⌘K</Kbd>
          <button
            type="button"
            aria-label="Preferences"
            title="Preferences"
            onClick={() => router.push("/preferences")}
            className={clsx(
              "grid h-[26px] w-[26px] cursor-pointer place-items-center rounded-[5px] border transition-colors",
              prefsActive
                ? "border-[color:color-mix(in_srgb,var(--accent)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_12px_color-mix(in_srgb,var(--accent)_18%,transparent)]"
                : "border-transparent text-[color:var(--fg-3)] hover:border-[color:var(--line-hi)] hover:bg-[color:color-mix(in_srgb,var(--accent)_5%,transparent)] hover:text-[color:var(--fg)]",
            )}
          >
            <svg
              viewBox="0 0 24 24"
              width="14"
              height="14"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              aria-hidden
            >
              <title>Preferences</title>
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3 1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8 1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
            </svg>
          </button>
          <button
            type="button"
            aria-label="Log out"
            title="Log out"
            disabled={loggingOut}
            onClick={handleLogout}
            className="grid h-[26px] w-[26px] cursor-pointer place-items-center rounded-[5px] border border-transparent text-[color:var(--fg-3)] transition-colors hover:border-[color:color-mix(in_srgb,var(--red)_45%,transparent)] hover:bg-[color:color-mix(in_srgb,var(--red)_10%,transparent)] hover:text-[color:var(--red)] disabled:cursor-default disabled:opacity-40"
          >
            <LogOut size={14} strokeWidth={1.8} aria-hidden />
          </button>
          <span>◉ ARPIT</span>
        </>
      }
    />
  );
}
