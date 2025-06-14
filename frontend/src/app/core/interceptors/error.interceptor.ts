import { HttpErrorResponse, HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { LoggingService } from '../services/logging.service';
import { UrlConfigService } from '../services/url-config.service';
import { NavigationService } from '../services/navigation.service';

// Paths that should not propagate errors to components (background/automatic operations)
const backgroundOperationsPaths = ['/auth/refresh/', '/auth/logout/'];

export const errorInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  const logger = inject(LoggingService);
  const urlConfigService = inject(UrlConfigService);
  const navigationService = inject(NavigationService);
  const apiUrl = urlConfigService.getApiUrl();

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      // Get request path for checking if it's a background operation
      let requestPath = request.url;
      if (request.url.startsWith(apiUrl)) {
        requestPath = request.url.slice(apiUrl.length);
      }

      // Check if this is a background operation (like refresh token)
      const isBackgroundOperation = backgroundOperationsPaths.some((path) => requestPath.includes(path));

      // Always log HTTP errors for debugging      logger.logHttpError(error, 'HttpInterceptor');

      // Handle different error statuses
      switch (error.status) {
        case 401:
          // Only logout if it's not already a logout request
          if (!requestPath.includes('/auth/logout/')) {
            authService.logout();
          }
          break;

        case 404:
          // Only redirect for user-facing requests, not background operations
          if (!isBackgroundOperation) {
            navigationService.navigateWithLang(['404']);
          }
          break;

        case 400:
          // Log validation errors but only propagate to components for user-facing requests
          if (isBackgroundOperation) {
            logger.debug('Background operation validation error - not propagated to component', error.error);
          } else {
            logger.debug('User validation error - propagated to component', error.error);
          }
          break;

        case 500:
          // Always log server errors
          logger.error('Server error occurred:', error.message);
          break;

        default:
          // Log other errors
          logger.warn(`Unhandled error code: ${error.status}`);
          break;
      }

      // Only propagate errors to components for user-facing requests
      // Background operations (like refresh token) should be handled internally
      if (isBackgroundOperation) {
        logger.debug(`Background operation error not propagated to component: ${requestPath}`);
        // Still throw the error but it won't reach user components due to auth interceptor handling
        return throwError(() => error);
      }

      // Propagate error to components for user-facing requests
      return throwError(() => error);
    })
  );
};
