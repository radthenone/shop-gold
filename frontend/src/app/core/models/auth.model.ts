import { User } from './user.model';

export type AuthUser = Pick<User, 'id' | 'email' | 'username' | 'role'>;

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse extends AuthTokens {
  user: AuthUser;
}

export type RegisterRequest = Omit<User, 'id' | 'is_active' | 'role'> & {
  password: string;
  rewrite_password: string;
};

export type LoginRequest = Pick<User, 'email'> & {
  password: string;
};
