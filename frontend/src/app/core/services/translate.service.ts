import { Injectable } from '@angular/core';
import { TranslateService as DefaultTranslateService } from '@ngx-translate/core';
import { UrlConfigService } from '@core/services/url-config.service';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class TranslateService {
  constructor(
    private translate: DefaultTranslateService,
    private urlConfigService: UrlConfigService,
    private router: Router
  ) {
    this.translate.addLangs(['pl', 'en']);
    const defaultLang = this.urlConfigService.getLanguage();
    this.translate.setDefaultLang(defaultLang);
    const browserLang = this.translate.getBrowserLang();
    const langToUse = browserLang?.match(/pl|en/) ? browserLang : defaultLang;
    this.translate.use(langToUse);

    if (this.urlConfigService.getLanguage() !== this.translate.currentLang) {
      this.urlConfigService.changeLanguage(this.translate.currentLang);
    }
  }

  translateFunctionAsync(key: string, params?: any): Promise<string> {
    return new Promise((resolve) => {
      this.translate.get(key, params).subscribe((translation: string) => {
        resolve(translation);
      });
    });
  }

  translateFunction(key: string, params?: any): string {
    return this.translate.instant(key, params);
  }

  setLanguage(newLang: string): void {
    const currentGlobalLang = this.urlConfigService.getLanguage();

    if (this.translate.currentLang === newLang && currentGlobalLang === newLang) {
      return;
    }

    this.translate.use(newLang);
    this.urlConfigService.changeLanguage(newLang);

    console.log('address', this.router.url);

    const currentUrl = this.router.url;
    let newUrl: string;

    const pathSegments = currentUrl.split('/').filter((segment) => segment.length > 0);

    if (pathSegments.length > 0 && (pathSegments[0] === 'en' || pathSegments[0] === 'pl')) {
      const basePath = pathSegments.slice(1).join('/');
      newUrl = `/${newLang}${basePath ? '/' + basePath : ''}`;
    } else {
      newUrl = `/${newLang}${currentUrl.startsWith('/') ? currentUrl : '/' + currentUrl}`;
      newUrl = newUrl.replace(/\/\//g, '/');
    }

    if (newUrl === `/${newLang}/` && currentUrl !== `/${currentGlobalLang}/`) {
      newUrl = `/${newLang}`;
    }
    if (!newUrl.startsWith('/')) {
      newUrl = '/' + newUrl;
    }

    if (newUrl !== currentUrl) {
      this.router.navigateByUrl(newUrl).then((success) => {
        if (!success) {
          console.error('Nawigacja do nowego URL językowego nie powiodła się.');
          this.translate.use(currentGlobalLang);
          this.urlConfigService.changeLanguage(currentGlobalLang);
        }
      });
    } else if (this.translate.currentLang !== newLang) {
      this.translate.use(newLang);
    }
  }

  getLanguage(): string {
    return this.translate.currentLang;
  }
}
