// Error handling interfaces
export interface ApiError {
  message: string;
  code?: string;
  field?: string;
  details?: any;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  errors?: ValidationError[];
  status_code: number;
}

export interface HttpErrorInfo {
  status: number;
  statusText: string;
  url: string;
  timestamp: string;
}

// Basic Django error with detail field (e.g., authentication errors)
export interface DetailError {
  detail: string;
}

// Django validation errors with field-specific errors
export interface DjangoError {
  [field: string]: string[] | undefined;
  non_field_errors?: string[];
  errors?: string[];
}

// Generic message error
export interface MessageError {
  message: string;
}

// Field-specific error for form validation
export interface FieldError {
  value: any;
  message: string;
  errorType: string;
}

// Union type for all possible error formats from backend
export type BackendError = DetailError | DjangoError | MessageError;

// Type guard functions to determine error type
export function isDetailError(error: any): error is DetailError {
  return error && typeof error.detail === 'string';
}

export function isDjangoError(error: any): error is DjangoError {
  return (
    error && (error.non_field_errors || error.errors || (typeof error === 'object' && !error.detail && !error.message))
  );
}

export function isMessageError(error: any): error is MessageError {
  return error && typeof error.message === 'string';
}
