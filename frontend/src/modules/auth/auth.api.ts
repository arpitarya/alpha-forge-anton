import api from "@/lib/api";

export async function login(username: string, password: string): Promise<void> {
  const body = new URLSearchParams({ username, password });
  const res = await api.post<{ access_token: string }>("/auth/token", body.toString(), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  localStorage.setItem("af_token", res.data.access_token);
}

export function logout(): void {
  localStorage.removeItem("af_token");
}
