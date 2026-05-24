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
