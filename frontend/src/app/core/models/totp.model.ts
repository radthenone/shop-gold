export interface TOTPStatus {
  is_enabled: boolean;
}

export interface TOTPSetup {
  qr_code_svg: string;
}

export interface TOTPResponse {
  access?: string;
  refresh?: string;
  user?: any;
  status?: string;
  recovery_codes?: string[];
  error?: string;
}

export interface TOTPVerifyResponse {
  success: boolean;
  message?: string;
  error?: string;
}
