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
      const pathSegments = window.location.pathname.split('/').filter((segment) => segment.length > 0);

      if (pathSegments.length >= 2) {
        const langCandidate = pathSegments[0];
        const versionCandidate = pathSegments[1];

        if (langCandidate.length === 2 && versionCandidate.startsWith('v')) {
          this.currentLangSubject.next(langCandidate);
          this.currentApiVersionSubject.next(versionCandidate);
          console.log(`Language set to: ${this.getLanguage()}, Version set to: ${this.getApiVersion()} from URL.`);
          return;
        }
      }
    } catch (error) {
      console.error('Error parsing language and version from URL:', error);
    }

    this.currentLangSubject.next(DEFAULT_LANG);
    this.currentApiVersionSubject.next(DEFAULT_API_VERSION);
    console.warn(`Using default language: ${this.getLanguage()}, default version: ${this.getApiVersion()}.`);
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
