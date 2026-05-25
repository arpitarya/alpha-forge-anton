import axios from "axios"

import type {
  ApiKey,
  ApiKeyCreateRequest,
  IamUser,
  LoginKeyResponse,
  LoginRequest,
  RegisterRequest,
  SessionResponse,
  TokenResponse,
} from "./auth.types"

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
})

// ── RSA helpers ───────────────────────────────────────────────────────────────

// PSS salt length must match backend/app/core/crypto.py _PSS_SALT = 32
const PSS_SALT = 32

let _cachedKey: LoginKeyResponse | null = null

function _pemToBytes(pem: string): Uint8Array<ArrayBuffer> {
  const b64 = pem
    .replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----/g, "")
    .replace(/\s/g, "")
  const raw = atob(b64)
  const bytes = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i)
  return bytes
}

async function _importPublicKey(pem: string, usage: KeyUsage[]): Promise<CryptoKey> {
  const keyBytes = _pemToBytes(pem)
  const algorithm = usage.includes("verify")
    ? { name: "RSA-PSS", hash: "SHA-256" }
    : { name: "RSA-OAEP", hash: "SHA-256" }
  return crypto.subtle.importKey("spki", keyBytes, algorithm, false, usage)
}

async function verifyModeSignature(key: LoginKeyResponse): Promise<boolean> {
  const cryptoKey = await _importPublicKey(key.public_key, ["verify"])
  const canonical = new TextEncoder().encode(`mode=${key.mode}&key_id=${key.key_id}`)
  const sigBytes = Uint8Array.from(atob(key.mode_signature), (c) => c.charCodeAt(0))
  return crypto.subtle.verify({ name: "RSA-PSS", saltLength: PSS_SALT }, cryptoKey, sigBytes, canonical)
}

async function getLoginKey(): Promise<LoginKeyResponse> {
  if (_cachedKey) return _cachedKey
  const res = await api.get<LoginKeyResponse>("/iam/login-key")
  const key = res.data
  if (!(await verifyModeSignature(key))) {
    throw new Error("Server mode signature invalid — possible MITM or key mismatch")
  }
  _cachedKey = key
  return key
}

/** Invalidate the cached public key (call after a server restart in dev or key rotation). */
export function invalidateLoginKey(): void {
  _cachedKey = null
}

async function encryptCredentials(
  publicKeyPem: string,
  credentials: LoginRequest,
): Promise<string> {
  const cryptoKey = await _importPublicKey(publicKeyPem, ["encrypt"])
  const payload = new TextEncoder().encode(
    JSON.stringify({ email: credentials.email, password: credentials.password }),
  )
  const ciphertext = await crypto.subtle.encrypt({ name: "RSA-OAEP" }, cryptoKey, payload)
  return btoa(String.fromCharCode(...new Uint8Array(ciphertext)))
}

// ── Auth API ──────────────────────────────────────────────────────────────────

export const registerUser = (body: RegisterRequest) =>
  api.post<IamUser>("/iam/register", body).then((r) => r.data)

export async function loginUser(credentials: LoginRequest): Promise<TokenResponse> {
  const keyInfo = await getLoginKey()

  if (keyInfo.mode === "prod") {
    const encrypted_payload = await encryptCredentials(keyInfo.public_key, credentials)
    return api.post<TokenResponse>("/iam/login", { encrypted_payload }).then((r) => r.data)
  }

  // dev: send plain — credentials are visible in DevTools (intentional)
  return api.post<TokenResponse>("/iam/login", credentials).then((r) => r.data)
}

export const refreshTokens = (refresh_token: string) =>
  api.post<TokenResponse>("/iam/refresh", { refresh_token }).then((r) => r.data)

export const logoutUser = (refresh_token: string) =>
  api.post("/iam/logout", { refresh_token }).then((r) => r.data)

export const getMe = () => api.get<IamUser>("/iam/me").then((r) => r.data)

export const createApiKey = (body: ApiKeyCreateRequest) =>
  api.post<ApiKey>("/iam/api-keys", body).then((r) => r.data)

export const listApiKeys = () => api.get<ApiKey[]>("/iam/api-keys").then((r) => r.data)

export const deleteApiKey = (id: string) =>
  api.delete(`/iam/api-keys/${id}`).then((r) => r.data)

export const listSessions = () =>
  api.get<SessionResponse[]>("/iam/sessions").then((r) => r.data)

export const extendSession = (id: string, extra_minutes?: number | null) =>
  api.post<SessionResponse>(`/iam/sessions/${id}/extend`, { extra_minutes }).then((r) => r.data)

export const revokeSession = (id: string) =>
  api.delete(`/iam/sessions/${id}`).then((r) => r.data)

export const logoutAll = () =>
  api.post("/iam/logout-all").then((r) => r.data)
