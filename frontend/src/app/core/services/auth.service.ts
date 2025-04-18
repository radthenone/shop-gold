import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import { User, AuthResponse, RegisterRequest } from '../models/user.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly API_URL = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    const user = localStorage.getItem('user');
    if (user) {
      this.currentUserSubject.next(JSON.parse(user));
    }
  }

  register(data: RegisterRequest): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(
      `${this.API_URL}/users/register/`,
      data
    );
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(
        `${this.API_URL}/users/login/`,
        { email, password },
        { withCredentials: true }
      );
  }

  completeLoginAfterMFA(response: any): void {
    // Set session with tokens and user data
    this.setSession(response);

    // Clear temporary login data
    sessionStorage.removeItem('temp_login_data');

    // Navigate to home page
    this.router.navigate(['/']);
  }

  logout(): void {
    // Make a POST request to the backend logout endpoint
    this.http.post(
      `${this.API_URL}/users/logout/`,
      {},
      { withCredentials: true }
    ).subscribe({
      next: () => {
        // Clear MFA data from session
        sessionStorage.removeItem('temp_login_data');
        // Clear all authentication data
        this.clearSession();
        // Navigate to login page
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        // Even if the backend request fails, clear local data and redirect
        sessionStorage.removeItem('temp_login_data');
        this.clearSession();
        this.router.navigate(['/auth/login']);
      }
    });
  }

  refreshToken(): Observable<{ access: string; refresh: string }> {
    const refresh = localStorage.getItem('refresh_token');
    return this.http
      .post<{ access: string; refresh: string }>(
        `${this.API_URL}/users/refresh/`,
        { refresh }
      )
      .pipe(
        tap((response) => {
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
        })
      );
  }

  verifyEmail(key: string): Observable<{ detail: string }> {
    return this.http.get<{ detail: string }>(
      `${this.API_URL}/users/verify-email/${key}/`
    );
  }

  resendEmail(email: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(
      `${this.API_URL}/users/resend-email/`,
      { email }
    );
  }

  checkEmail(): Observable<{ detail: string }> {
    return this.http.get<{ detail: string }>(
      `${this.API_URL}/users/check-email/`
    );
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
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
      this.currentUserSubject.next(response.user);
    }
  }

  private clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('temp_login_data');
    this.currentUserSubject.next(null);
  }
}
