import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { TOTPStatus, TOTPSetup, TOTPResponse } from '../models/totp.model';

@Injectable({
  providedIn: 'root',
})
export class TOTPService {
  private readonly API_URL = `${environment.apiUrl}/users/totp`;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    });
  }

  getStatus(): Observable<TOTPStatus> {
    return this.http.get<TOTPStatus>(`${this.API_URL}/status/`, {
      headers: this.getHeaders(),
    });
  }

  setup(): Observable<TOTPSetup> {
    return this.http.post<TOTPSetup>(
      `${this.API_URL}/setup/`,
      {},
      { headers: this.getHeaders(), withCredentials: true }
    );
  }

  activate(code: string): Observable<TOTPResponse> {
    const sanitizedCode = code.trim().replace(/\s/g, '');

    if (!/^\d{6}$/.test(sanitizedCode)) {
      return throwError(() => new Error('Kod musi składać się z 6 cyfr'));
    }

    return this.http
      .post<TOTPResponse>(
        `${this.API_URL}/activate/`,
        { code: sanitizedCode },
        { headers: this.getHeaders(), withCredentials: true }
      )
      .pipe(
        catchError((error) => {
          if (error.status === 400) {
            const message =
              error.error?.detail || error.error?.error || 'Nieprawidłowy kod';
            return throwError(() => new Error(message));
          }
          return throwError(
            () => new Error('Wystąpił błąd podczas aktywacji TOTP')
          );
        })
      );
  }

  verify(code: string): Observable<TOTPResponse> {
    const sanitizedCode = code.trim().replace(/\s/g, '');

    if (!/^\d{6}$/.test(sanitizedCode)) {
      return throwError(() => new Error('Kod musi składać się z 6 cyfr'));
    }

    // Check if this is MFA during login (no token yet)
    const isMFALogin = !localStorage.getItem('access_token') &&
                       sessionStorage.getItem('temp_login_data');

    // For MFA login, don't include Authorization header
    const options = isMFALogin
      ? { withCredentials: true }
      : { headers: this.getHeaders(), withCredentials: true };

    return this.http
      .post<TOTPResponse>(
        `${this.API_URL}/verify/`,
        { code: sanitizedCode },
        options
      )
      .pipe(
        catchError((error) => {
          if (error.status === 400) {
            const message =
              error.error?.detail || error.error?.error || 'Nieprawidłowy kod';
            return throwError(() => new Error(message));
          }
          return throwError(
            () => new Error('Wystąpił błąd podczas weryfikacji kodu')
          );
        })
      );
  }

  verifyRecoveryCode(code: string): Observable<TOTPResponse> {
    // Check if this is MFA during login (no token yet)
    const isMFALogin = !localStorage.getItem('access_token') &&
                       sessionStorage.getItem('temp_login_data');

    // For MFA login, don't include Authorization header
    const options = isMFALogin
      ? { withCredentials: true }
      : { headers: this.getHeaders(), withCredentials: true };

    return this.http.post<TOTPResponse>(
      `${this.API_URL}/verify-recovery-code/`,
      { code },
      options
    ).pipe(
      catchError((error) => {
        if (error.status === 400) {
          const message =
            error.error?.detail || error.error?.error || 'Nieprawidłowy kod odzyskiwania';
          return throwError(() => new Error(message));
        }
        return throwError(
          () => new Error('Wystąpił błąd podczas weryfikacji kodu odzyskiwania')
        );
      })
    );
  }

  getRecoveryCodes(): Observable<{ recovery_codes: string[] }> {
    return this.http.get<{ recovery_codes: string[] }>(
      `${this.API_URL}/recovery-codes/`,
      { headers: this.getHeaders() }
    );
  }

  generateNewRecoveryCodes(): Observable<{ recovery_codes: string[] }> {
    return this.http.post<{ recovery_codes: string[] }>(
      `${this.API_URL}/generate-recovery-codes/`,
      {},
      { headers: this.getHeaders() }
    );
  }

  deactivate(): Observable<TOTPResponse> {
    return this.http.post<TOTPResponse>(
      `${this.API_URL}/deactivate/`,
      {},
      { headers: this.getHeaders() }
    );
  }
}
