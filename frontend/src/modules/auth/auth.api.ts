import axios from "axios"

import type {
  ApiKey,
  ApiKeyCreateRequest,
  IamUser,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
} from "./auth.types"

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
})

export const registerUser = (body: RegisterRequest) =>
  api.post<IamUser>("/iam/register", body).then((r) => r.data)

export const loginUser = (body: LoginRequest) =>
  api.post<TokenResponse>("/iam/login", body).then((r) => r.data)

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
