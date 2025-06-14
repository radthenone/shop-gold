import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { BehaviorSubject, Observable } from 'rxjs';

const DEFAULT_LANG = environment.defaultLang;
const DEFAULT_API_VERSION = environment.defaultApiVersion;

@Injectable({
  providedIn: 'root',
})
export class UrlConfigService {
  private currentLangSubject: BehaviorSubject<string> = new BehaviorSubject<string>(DEFAULT_LANG);
  private currentApiVersionSubject: BehaviorSubject<string> = new BehaviorSubject<string>(DEFAULT_API_VERSION);
  public currentLang$: Observable<string> = this.currentLangSubject.asObservable();
  public currentApiVersion$: Observable<string> = this.currentApiVersionSubject.asObservable();

  constructor() {
    this.parseUrlPath();
  }

  private parseUrlPath(): void {
    try {
      const pathname = window.location.pathname;

      const pathSegments = pathname.split('/').filter((segment) => segment.length > 0);

      if (pathSegments.length >= 1) {
        const langCandidate = pathSegments[0];

        // Check if the first segment is a valid language code
        if (langCandidate.length === 2 && ['pl', 'en'].includes(langCandidate)) {
          this.currentLangSubject.next(langCandidate);

          // Check if there's also a version in the URL (for API calls)
          if (pathSegments.length >= 2 && pathSegments[1].startsWith('v')) {
            this.currentApiVersionSubject.next(pathSegments[1]);
          } else {
            this.currentApiVersionSubject.next(DEFAULT_API_VERSION);
          }
          return;
        }
      }
    } catch (error) {
      // Error parsing language and version from URL
    }

    this.currentLangSubject.next(DEFAULT_LANG);
    this.currentApiVersionSubject.next(DEFAULT_API_VERSION);
  }

  public changeLanguage(lang: string): void {
    this.currentLangSubject.next(lang);
  }

  public getLanguage(): string {
    return this.currentLangSubject.value;
  }

  public getApiVersion(): string {
    return this.currentApiVersionSubject.value;
  }

  public getApiUrl(): string {
    return `${environment.backendUrl}/${this.getLanguage()}/api/${this.getApiVersion()}`;
  }

  public getWsUrl(): string {
    return environment.wsUrl;
  }
}
