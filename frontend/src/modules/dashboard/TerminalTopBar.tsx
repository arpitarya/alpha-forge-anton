"use client";

import { Kbd, LiveDot, Logo, TopBar, type TopBarNavItem } from "@alphaforge/solar-orb-ui";
import { usePathname, useRouter } from "next/navigation";

const NAV_ITEMS: Array<{ id: string; label: string; href: string }> = [
  { id: "terminal", label: "Terminal", href: "/" },
  { id: "portfolio", label: "Portfolio", href: "/portfolio" },
];

function isActive(pathname: string | null, href: string): boolean {
  if (!pathname) return href === "/";
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TerminalTopBar() {
  const router = useRouter();
  const pathname = usePathname();

  const nav: TopBarNavItem[] = NAV_ITEMS.map((n) => ({
    id: n.id,
    label: n.label,
    active: isActive(pathname, n.href),
    onClick: () => router.push(n.href),
  }));

  return (
    <TopBar
      brand={
        <>
          <div style={{ filter: "drop-shadow(0 0 12px var(--glow))" }}>
            <Logo variant="icon" size="xs" />
          </div>
          <div className="flex flex-col gap-[2px] leading-none">
            <span className="font-[800] tracking-[0.18em] text-[13px] text-[color:var(--fg)]">ALPHA</span>
            <span className="font-[500] tracking-[0.32em] text-[10px] text-[color:var(--fg-3)]">FORGE</span>
          </div>
        </>
      }
      nav={nav}
      right={
        <>
          <LiveDot label="LIVE · NSE" />
          <Kbd>⌘K</Kbd>
          <span>◉ ARPIT</span>
        </>
      }
    />
  );
}
