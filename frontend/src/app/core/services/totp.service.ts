import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError, BehaviorSubject, tap } from 'rxjs';
import {
  TotpActivateRequest,
  TotpActivateResponse,
  TotpRecoveryCodeRequest,
  TotpSetupResponse,
  TotpStatusResponse,
  TotpVerifyRequest,
} from '../interfaces/api/totp.interface';
import { AuthResponse } from '../interfaces/api/auth.interface';
import { AuthService, UrlConfigService } from '@core/services';

@Injectable({
  providedIn: 'root',
})
export class TOTPService {
  private get API_URL(): string {
    return this.urlConfigService.getApiUrl();
  }

  private _isTotpEnabledSubject = new BehaviorSubject<boolean>(false);
  public isTotpEnabled$ = this._isTotpEnabledSubject.asObservable();

  public get isTotpEnabled(): boolean {
    return this._isTotpEnabledSubject.value;
  }

  constructor(
    private http: HttpClient,
    private urlConfigService: UrlConfigService,
    private authService: AuthService
  ) {}

  // Helper private method for code validation
  private _isValidCodeFormat(code: string): boolean {
    const sanitizedCode = code.trim().replace(/\s/g, '');
    const regexCode = /^\d{6}$/;
    return regexCode.test(sanitizedCode);
  }

  // Helper private method to get sanitized code
  private _sanitizeCode(code: string): string {
    return code.trim().replace(/\s/g, '');
  }

  public loadTotpStatus(): void {
    this.getStatus().subscribe({
      next: (status) => {
        this._isTotpEnabledSubject.next(status.is_enabled);
      },
      error: () => {
        this._isTotpEnabledSubject.next(false);
      },
    });
  }

  getStatus(): Observable<TotpStatusResponse> {
    return this.http.get<TotpStatusResponse>(`${this.API_URL}/auth/totp/status/`);
  }

  setup(): Observable<TotpSetupResponse> {
    return this.http.get<TotpSetupResponse>(`${this.API_URL}/auth/totp/setup/`);
  }

  activate({ code: totpCode }: TotpActivateRequest): Observable<TotpActivateResponse> {
    if (!this._isValidCodeFormat(totpCode)) {
      return throwError(() => new Error('Code must be 6 digits long'));
    }
    const sanitizedCode = this._sanitizeCode(totpCode);

    return this.http
      .post<TotpActivateResponse>(`${this.API_URL}/auth/totp/activate/`, {
        code: sanitizedCode,
      })
      .pipe(
        catchError((error) => {
          if (error.status === 400) {
            const message = error.error?.detail || error.error?.error || 'Wrong code';
            return throwError(() => new Error(message));
          }
          return throwError(() => new Error('Wrong activation code'));
        })
      );
  }

  verify({ code }: TotpVerifyRequest): Observable<AuthResponse> {
    if (!this._isValidCodeFormat(code)) {
      return throwError(() => new Error('Code must be 6 digits long'));
    }
    const sanitizedCode = this._sanitizeCode(code);

    return this.http.post<AuthResponse>(`${this.API_URL}/auth/totp/verify/`, { code: sanitizedCode }).pipe(
      tap((response) => {
        this.authService.setSession(response);
      }),
      catchError((error) => {
        if (error.status === 400) {
          const message = error.error?.detail || error.error?.error || 'Wrong code';
          return throwError(() => new Error(message));
        }
        return throwError(() => new Error('Invalid verification code'));
      })
    );
  }

  verifyRecoveryCode({ code }: TotpRecoveryCodeRequest): Observable<AuthResponse> {
    if (!this._isValidCodeFormat(code)) {
      return throwError(() => new Error('Code must be 6 digits long'));
    }
    const sanitizedCode = this._sanitizeCode(code);

    return this.http
      .post<AuthResponse>(`${this.API_URL}/auth/totp/verify-recovery-code/`, { code: sanitizedCode })
      .pipe(
        tap((response) => {
          this.authService.setSession(response);
        }),
        catchError((error) => {
          if (error.status === 400) {
            const message = error.error?.detail || error.error?.error || 'Wrong code';
            return throwError(() => new Error(message));
          }
          return throwError(() => new Error('Invalid recovery code'));
        })
      );
  }

  getRecoveryCodes(): Observable<{ recovery_codes: string[] }> {
    return this.http.get<{ recovery_codes: string[] }>(`${this.API_URL}/auth/totp/recovery-codes/`);
  }

  generateNewRecoveryCodes(): Observable<{ recovery_codes: string[] }> {
    return this.http.post<{ recovery_codes: string[] }>(`${this.API_URL}/auth/totp/generate-recovery-codes/`, {}).pipe(
      catchError((error) => {
        if (error.status === 400) {
          const message = error.error?.detail || error.error?.error || 'Error generating codes';
          return throwError(() => new Error(message));
        }
        return throwError(() => new Error('Failed to generate new recovery codes'));
      })
    );
  }

  deactivate(): Observable<{ status: boolean }> {
    return this.http.post<{ status: boolean }>(`${this.API_URL}/auth/totp/deactivate/`, {});
  }
}
