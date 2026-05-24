"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuthStore } from "./useAuthStore";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isLogin = pathname === "/login";
  const [ready, setReady] = useState(isLogin);
  const { accessToken, bootstrap } = useAuthStore();

  useEffect(() => {
    if (isLogin) {
      setReady(true);
      return;
    }
    if (!accessToken) {
      router.replace("/login");
      return;
    }
    bootstrap().finally(() => setReady(true));
  }, [isLogin, accessToken, bootstrap, router]);

  if (!ready) return null;
  return <>{children}</>;
}
