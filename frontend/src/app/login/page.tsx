"use client";

import { Logo } from "@alphaforge-anton/solar-ui";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getMe, loginUser } from "@/modules/auth/auth.api";
import { useAuthStore } from "@/modules/auth/useAuthStore";

export default function LoginPage() {
  const router = useRouter();
  const { accessToken, setTokens, setUser } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (accessToken) router.replace("/");
  }, [accessToken, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await loginUser({ email, password });
      setTokens(tokens);
      setUser(await getMe());
      router.replace("/");
    } catch {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen items-center justify-center bg-black">
      <form
        onSubmit={handleSubmit}
        className="flex w-80 flex-col gap-5 rounded border border-white/10 bg-black/80 p-8"
        style={{ backdropFilter: "blur(12px)" }}
      >
        <div className="flex flex-col gap-3">
          <Logo variant="lockup" size="sm" />
          <h1 className="font-mono text-base" style={{ color: "var(--fg-2)" }}>
            Terminal Access
          </h1>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="email" className="font-mono text-xs" style={{ color: "var(--fg-3)" }}>
            EMAIL
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
            className="rounded border px-3 py-2 font-mono text-sm outline-none"
            style={{
              background: "var(--surface-2)",
              borderColor: "var(--line)",
              color: "var(--fg)",
            }}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="font-mono text-xs" style={{ color: "var(--fg-3)" }}>
            PASSWORD
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            className="rounded border px-3 py-2 font-mono text-sm outline-none"
            style={{
              background: "var(--surface-2)",
              borderColor: "var(--line)",
              color: "var(--fg)",
            }}
          />
        </div>

        {error && (
          <p className="font-mono text-xs" style={{ color: "var(--error, #f87171)" }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="mt-1 rounded py-2 font-mono text-sm transition-opacity disabled:opacity-50"
          style={{
            background: "color-mix(in srgb, var(--accent) 15%, transparent)",
            border: "1px solid color-mix(in srgb, var(--accent) 40%, transparent)",
            color: "var(--accent)",
          }}
        >
          {loading ? "Authenticating…" : "Access Terminal"}
        </button>
      </form>
    </div>
  );
}
