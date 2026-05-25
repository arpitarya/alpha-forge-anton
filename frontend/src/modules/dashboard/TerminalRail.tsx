"use client";

import { IconRail } from "@alphaforge-anton/solar-ui";
import { usePathname, useRouter } from "next/navigation";

const ITEMS = [
  { id: "terminal", icon: "terminal", label: "Terminal", href: "/" },
  { id: "portfolio", icon: "account_balance_wallet", label: "Portfolio", href: "/portfolio" },
];

function isActive(pathname: string | null, href: string): boolean {
  if (!pathname) return href === "/";
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TerminalRail() {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <IconRail
      items={ITEMS.map((i) => ({
        id: i.id,
        icon: i.icon,
        label: i.label,
        active: isActive(pathname, i.href),
        onClick: () => router.push(i.href),
      }))}
    />
  );
}
