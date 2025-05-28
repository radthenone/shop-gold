import { Injectable, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthTokens, AuthResponse, AuthUser, RegisterRequest, LoginRequest } from '../models/auth.model';
import { MfaResponse } from '../models/totp.model';
import { UrlConfigService } from './url-config.service';
import { LoggingService } from './logging.service';

@Injectable({
  providedIn: 'root',
})
export class AuthService implements OnDestroy {
  private API_URL: string;
  private userSubject = new BehaviorSubject<AuthUser | null>(null);
  public user$ = this.userSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router,
    private urlConfigService: UrlConfigService,
    private loggingService: LoggingService
  ) {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        this.userSubject.next(JSON.parse(user));
      } catch (error) {
        this.userSubject.next(null);
      }
    }
    window.addEventListener('storage', this.storageEventListener);
    this.API_URL = this.urlConfigService.getApiUrl();
    this.loggingService.info('API URL:', this.API_URL);
  }

  ngOnDestroy(): void {
    window.removeEventListener('storage', this.storageEventListener);
  }

  public get userValue(): AuthUser | null {
    return this.userSubject.value;
  }

  public getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  register(data: RegisterRequest): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.API_URL}/auth/register/`, data);
  }

  login(data: LoginRequest): Observable<AuthResponse | MfaResponse> {
    return this.http
      .post<AuthResponse | MfaResponse>(`${this.API_URL}/auth/login/`, { email: data.email, password: data.password })
      .pipe(
        tap((response) => {
          if ('access' in response && 'refresh' in response) {
            this.setSession(response);
          }
        })
      );
  }

  logout(): void {
    const token = this.getAuthToken();

    if (!token) {
      this.clearSession();
      this.router.navigate(['/auth/login']).then();
      return;
    }

    this.http.post(`${this.API_URL}/auth/logout/`, {}).subscribe({
      next: () => {
        this.clearSession();
        this.router.navigate(['/auth/login']).then();
      },
      error: () => {
        this.clearSession();
        this.router.navigate(['/auth/login']).then();
      },
    });
  }

  refreshToken(): Observable<AuthTokens> {
    const refresh = localStorage.getItem('refresh_token');
    return this.http.post<AuthTokens>(`${this.API_URL}/auth/refresh/`, { refresh }).pipe(
      tap((response) => {
        this.setRefreshSession(response);
      })
    );
  }

  verifyEmail(key: string): Observable<{ detail: string }> {
    return this.http.get<{ detail: string }>(`${this.API_URL}/auth/verify_email/${key}/`);
  }

  resendEmail(email: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.API_URL}/auth/resend_email/`, { email });
  }

  checkEmail(email: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.API_URL}/auth/check_email/`, { email });
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  private setRefreshSession(response: AuthTokens): void {
    if (response.access) {
      localStorage.setItem('access_token', response.access);
    }
    if (response.refresh) {
      localStorage.setItem('refresh_token', response.refresh);
    }
  }

  private setSession(response: AuthResponse): void {
    if (response.access) {
      localStorage.setItem('access_token', response.access);
    }
    if (response.refresh) {
      localStorage.setItem('refresh_token', response.refresh);
    }
    if (response.user) {
      localStorage.setItem('user', JSON.stringify(response.user));
      this.userSubject.next(response.user);
    }
  }

  private clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    this.userSubject.next(null);
  }

  private storageEventListener = (event: StorageEvent) => {
    if (event.key === 'user' && event.storageArea === localStorage) {
      try {
        const user = event.newValue ? JSON.parse(event.newValue) : null;
        if (JSON.stringify(this.userSubject.value) !== JSON.stringify(user)) {
          this.userSubject.next(user);
        }
      } catch (error) {
        this.userSubject.next(null);
      }
    }
  };
}
