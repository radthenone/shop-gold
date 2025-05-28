export interface DjangoError {
  [key: string]: string[] | undefined;
  non_field_errors?: string[];
}
export interface MessageError {
  message: string;
}

export interface FieldError {
  value: boolean;
  message: string;
  errorType: string | null;
}
