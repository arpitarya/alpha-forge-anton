export type Role = "owner" | "viewer"

export interface IamUser {
  id: string
  email: string
  full_name: string
  role: Role
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  role?: Role
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginKeyResponse {
  public_key: string
  algorithm: string
  key_id: string
  mode: "dev" | "prod"
  mode_signature: string  // RSA-PSS-SHA256 over "mode={mode}&key_id={key_id}"
  mode_path: string       // dynamic path to the mode endpoint
}

export interface SessionResponse {
  id: string
  created_at: string
  last_active_at: string
  expires_at: string
  idle_expires_at: string
  revoked: boolean
  ip_address: string | null
  device_hint: string | null
}

export interface ApiKeyCreateRequest {
  label: string
  role?: Role
  expires_days?: number | null
}

export interface ApiKey {
  id: string
  label: string
  key_prefix: string
  role: Role
  expires_at: string | null
  created_at: string
  raw_key?: string
}
