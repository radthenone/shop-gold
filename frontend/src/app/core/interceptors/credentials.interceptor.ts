import { HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

const urlsWithCredentials: string[] = [
  '/auth/login/',
  '/auth/totp/setup/',
  '/auth/totp/activate/',
  '/auth/totp/verify/',
  '/auth/totp/verify-recovery-code/',
];

export const credentialsInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  if (urlsWithCredentials.includes(request.url)) {
    request = request.clone({ withCredentials: true });
  }
  return next(request);
};
