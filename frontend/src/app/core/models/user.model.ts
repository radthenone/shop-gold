export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  username: string;
  role: string;
}

export interface AuthResponse {
  access?: string;
  refresh?: string;
  user?: User;
  mfa_required?: boolean;
  detail?: string;
}

export interface RegisterRequest {
  email: string;
  password1: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}
