// Common type definitions and type aliases

// Generic API response wrapper
export type ApiResponse<T = any> = {
  data: T;
  message?: string;
  status: 'success' | 'error';
};

// Pagination types
export type PaginationMeta = {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
};

export type PaginatedResponse<T> = {
  items: T[];
  meta: PaginationMeta;
};

// Common status types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
export type Theme = 'light' | 'dark' | 'auto';
export type Language = 'en' | 'pl';

// Form validation types
export type ValidationResult = {
  isValid: boolean;
  errors: string[];
};

// Generic ID types
export type ID = string | number;
export type UUID = string;

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
