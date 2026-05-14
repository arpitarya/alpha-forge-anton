"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { login } from "@/modules/auth/auth.api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("af_token")) router.replace("/");
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
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
        <div className="flex flex-col gap-1">
          <span className="font-mono text-xs" style={{ color: "var(--accent)" }}>
            ALPHAFORGE
          </span>
          <h1 className="font-mono text-lg" style={{ color: "var(--fg)" }}>
            Terminal Access
          </h1>
        </div>

        <div className="flex flex-col gap-1">
          <label className="font-mono text-xs" style={{ color: "var(--fg-3)" }}>
            USERNAME
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
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
          <label className="font-mono text-xs" style={{ color: "var(--fg-3)" }}>
            PASSWORD
          </label>
          <input
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
