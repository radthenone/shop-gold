import { HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UrlConfigService } from '../services/url-config.service';
import { inject } from '@angular/core';

export const langInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const urlConfigService = inject(UrlConfigService);
  const langReq = request.clone({
    setHeaders: { 'Accept-Language': urlConfigService.getLanguage() },
  });
  return next(langReq);
};
