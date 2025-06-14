import { HttpErrorResponse, HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { BehaviorSubject, catchError, filter, finalize, Observable, switchMap, take, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { UrlConfigService } from '../services/url-config.service';

let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

const exceptionsPaths = [
  '/auth/register/',
  '/auth/login/',
  '/auth/refresh/',
  '/auth/logout/',
  '/auth/totp/verify/',
  '/auth/totp/verify-recovery-code/',
  '/auth/check-email/',
];

export const authInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const urlConfigService = inject(UrlConfigService);
  const authService = inject(AuthService);
  const token = authService.getAuthToken();
  const apiUrl = urlConfigService.getApiUrl();

  let requestPath = request.url;
  if (request.url.startsWith(apiUrl)) {
    requestPath = request.url.slice(apiUrl.length);
  }

  if (token) {
    let shouldAddToken = true;
    for (const path of exceptionsPaths) {
      if (requestPath.includes(path)) {
        shouldAddToken = false;
        break;
      }
    }

    if (shouldAddToken) {
      request = addJwtToken(request, token);
    }
  }

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        const shouldAttemptRefresh = !exceptionsPaths.some((path) => requestPath.includes(path));

        if (shouldAttemptRefresh) {
          return handle401Error(request, next, authService);
        }
      }

      return throwError(() => error);
    })
  );
};

function addJwtToken(request: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return request.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });
}

function handle401Error(request: HttpRequest<unknown>, next: HttpHandlerFn, authService: AuthService) {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);

    return authService.refreshToken().pipe(
      switchMap((response) => {
        isRefreshing = false;
        refreshTokenSubject.next(response.access);
        return next(addJwtToken(request, response.access));
      }),
      catchError(() => {
        isRefreshing = false;
        refreshTokenSubject.next(null);

        // Logout user when refresh token fails
        authService.logout();

        // Don't propagate refresh token errors to components
        // Return the original 401 error instead of the refresh error
        return throwError(
          () =>
            new HttpErrorResponse({
              error: { detail: 'Session expired. Please log in again.' },
              status: 401,
              statusText: 'Unauthorized',
            })
        );
      }),
      finalize(() => {
        isRefreshing = false;
      })
    );
  } else {
    return refreshTokenSubject.pipe(
      filter((token) => token !== null),
      take(1),
      switchMap((token) => {
        return next(addJwtToken(request, token as string));
      })
    );
  }
}
