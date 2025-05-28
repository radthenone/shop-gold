import { HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { inject } from '@angular/core';
import { UrlConfigService } from '../services/url-config.service';

export const versionInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const urlConfigService = inject(UrlConfigService);
  const versionedReq = request.clone({
    setHeaders: { 'x-api-version': urlConfigService.getApiVersion() },
  });
  return next(versionedReq);
};
