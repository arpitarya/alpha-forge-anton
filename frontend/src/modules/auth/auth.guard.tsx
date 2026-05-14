"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isLogin = pathname === "/login";
  const [ready, setReady] = useState(isLogin);

  useEffect(() => {
    if (isLogin) {
      setReady(true);
      return;
    }
    const token = localStorage.getItem("af_token");
    if (!token) {
      router.replace("/login");
    } else {
      setReady(true);
    }
  }, [isLogin, router]);

  if (!ready) return null;
  return <>{children}</>;
}
