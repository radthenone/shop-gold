// Navigation state interfaces for routing and state management
export interface MessageState {
  successMessage?: string;
  errorMessage?: string;
}

export interface UserState {
  userInfo?: {
    id: number;
    name: string;
    email: string;
  };
  isLoggedIn?: boolean;
  permissions?: string[];
}

export interface ErrorState {
  errorCode?: number;
  errorDetails?: string;
  timestamp?: string;
  redirectUrl?: string;
}
