import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { TranslateService as NgxTranslateService } from '@ngx-translate/core';
import { UrlConfigService } from '@core/services/url-config.service';
import { switchMap, take } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class TranslationGuard implements CanActivate {
  constructor(
    private translate: NgxTranslateService,
    private urlConfigService: UrlConfigService,
    private router: Router
  ) {}
  canActivate(): Observable<boolean> {
    const language = this.urlConfigService.getLanguage();

    // Ensure translations are loaded before proceeding
    return this.translate.use(language).pipe(
      take(1),
      switchMap(() => {
        return of(true);
      })
    );
  }
}
