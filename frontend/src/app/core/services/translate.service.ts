import { Injectable } from '@angular/core';
import { TranslateService as DefaultTranslateService } from '@ngx-translate/core';
import { UrlConfigService } from '@core/services/url-config.service';
import { Router } from '@angular/router';
import { combineLatest } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class TranslateService {
  constructor(
    private translate: DefaultTranslateService,
    private urlConfigService: UrlConfigService,
    private router: Router
  ) {
    // Initialize supported languages
    this.translate.addLangs(['pl', 'en']);

    // Get language from URL
    const langFromUrl = this.urlConfigService.getLanguage();

    // Set default language
    this.translate.setDefaultLang(langFromUrl);

    // Load both static and backend translations
    this.loadAllTranslations(langFromUrl);
  }

  /**
   * Load both static translations and backend translations
   */
  private loadAllTranslations(language: string): void {
    // Load static translations from JSON files
    const staticTranslations$ = this.translate.use(language);

    // Combine both translation sources
    combineLatest([staticTranslations$]).subscribe({
      next: ([staticTranslations]) => {
        // Set the static translations
        this.translate.setTranslation(language, staticTranslations, true);

        console.log(`All translations loaded successfully for language: ${language}`);
      },
      error: (error) => {
        console.error(`Error loading translations for ${language}:`, error);
        // Fallback to static translations only
        this.translate.use(language);
      },
    });
  }

  translateFunctionAsync(key: string, params?: any): Promise<string> {
    return new Promise((resolve) => {
      this.translate.get(key, params).subscribe((translation: string) => {
        resolve(translation);
      });
    });
  }

  translateFunction(key: string, params?: any): string {
    // Check if translations are loaded for the key
    const translationWithoutParams = this.translate.instant(key);

    // Manual interpolation as workaround for ngx-translate parameter issues
    if (params && translationWithoutParams !== key) {
      let manualResult = translationWithoutParams;
      Object.keys(params).forEach((paramKey) => {
        manualResult = manualResult.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), params[paramKey]);
      });
      return manualResult;
    }

    // Try with params first
    const result = this.translate.instant(key, params);

    // Check if translations are loaded
    if (result === key) {
      // Translation not found for key
      // Fallback: try manual interpolation with key
      if (params) {
        let fallbackResult = key;
        Object.keys(params).forEach((paramKey) => {
          fallbackResult = fallbackResult.replace(`{${paramKey}}`, params[paramKey]);
        });
        return fallbackResult;
      }
    }

    return result;
  }

  setLanguage(newLang: string): void {
    const currentGlobalLang = this.urlConfigService.getLanguage();

    if (this.translate.currentLang === newLang && currentGlobalLang === newLang) {
      return;
    }

    // Load all translations for the new language
    this.loadAllTranslations(newLang);
    this.urlConfigService.changeLanguage(newLang);

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
          // Navigation to new language URL failed
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
