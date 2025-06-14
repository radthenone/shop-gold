// Authentication API interfaces
export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  first_name: string;
  last_name: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: AuthUser;
  access: string;
  refresh: string;
  mfa_required?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface RegisterResponse {
  detail: string;
  user_id: number;
}

export interface ResendEmailRequest {
  email: string;
}

export interface ResendEmailResponse {
  detail: string;
}

export interface VerifyEmailRequest {
  token: string;
}

export interface VerifyEmailResponse {
  detail: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  detail: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  password: string;
  password_confirm: string;
}

export interface PasswordResetConfirmResponse {
  detail: string;
}
