// User-related interfaces
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface UserProfile {
  user: User;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  postal_code?: string;
}

export interface UserUpdateRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  postal_code?: string;
}
