export interface MfaResponse {
  mfa_required: boolean;
}

export interface TotpStatusResponse {
  is_enabled: boolean;
}

export interface TotpSetupResponse {
  secret: string;
  qr_code: string;
}

export interface TotpActivateRequest {
  code: string;
}

export interface TotpActivateResponse {
  status: string;
  recovery_codes: string[];
}

export interface TotpVerifyRequest extends TotpActivateRequest {}

export interface TotpRecoveryCodeRequest extends TotpActivateRequest {}
