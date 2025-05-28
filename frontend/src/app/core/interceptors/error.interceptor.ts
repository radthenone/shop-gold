import { HttpErrorResponse, HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { LoggingService } from '../services/logging.service';

export const errorInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const logger = inject(LoggingService);

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      // Logowanie wszystkich błędów HTTP
      logger.logHttpError(error, 'HttpInterceptor');

      switch (error.status) {
        case 401:
          // Nieautoryzowany - wyloguj użytkownika
          authService.logout();
          break;

        case 404:
          // Nie znaleziono - przekieruj na stronę 404
          router.navigate(['/404']).then();
          break;

        case 400:
          // Błędy walidacji - loguj szczegóły i przekaż do komponentu
          logger.debug('Błąd walidacji - przekazany do obsługi w komponencie', error.error);
          break;

        case 500:
          // Błędy serwera
          logger.error('Wystąpił błąd serwera:', error.message);
          break;

        default:
          // Inne błędy
          logger.warn(`Nieobsłużony kod błędu: ${error.status}`);
          break;
      }

      // Przekaż błąd dalej do obsługi w komponentach
      return throwError(() => error);
    })
  );
};
