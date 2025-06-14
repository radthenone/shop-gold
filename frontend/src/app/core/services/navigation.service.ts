// typed-navigation-state.service.ts
import { Injectable } from '@angular/core';
import { Router, NavigationExtras } from '@angular/router';
import { UrlConfigService } from './url-config.service';
import { LoggingService } from './logging.service';

@Injectable({
  providedIn: 'root',
})
export class NavigationService {
  constructor(
    private router: Router,
    private urlConfigService: UrlConfigService,
    private logService: LoggingService
  ) {}

  // Navigate with current language prefix
  navigateWithLang(route: string[], extras?: NavigationExtras): Promise<boolean> {
    const currentLang = this.urlConfigService.getLanguage();
    const routeWithLang = [currentLang, ...route];

    // Debug logging to help identify problematic navigation calls
    this.logService.info('NavigationService.navigateWithLang called with:', {
      originalRoute: route,
      finalRoute: routeWithLang,
      stackTrace: new Error().stack,
    });

    return this.router.navigate(routeWithLang, extras);
  }

  // Set state with language prefix navigation
  setStateWithLang(route: string[], stateObject: { [key: string]: any }, delay: number = 0): void {
    const navigationExtras: NavigationExtras = {
      state: stateObject,
    };

    if (delay > 0) {
      setTimeout(() => {
        this.navigateWithLang(route, navigationExtras);
      }, delay);
    } else {
      this.navigateWithLang(route, navigationExtras);
    }
  }

  // Metoda z typowanym obiektem stanu
  setState(
    route: string[],
    stateObject: {
      [key: string]: any;
    },
    delay: number = 0
  ): void {
    const navigationExtras: NavigationExtras = {
      state: stateObject,
    };

    if (delay > 0) {
      setTimeout(() => {
        this.router.navigate(route, navigationExtras);
      }, delay);
    } else {
      this.router.navigate(route, navigationExtras);
    }
  }

  // Odczytywanie typowanego stanu
  getState(): Record<string, unknown> | null {
    const navigation = this.router.getCurrentNavigation();
    return (navigation?.extras.state as Record<string, unknown>) || null;
  }

  isStateValid(key: string): boolean {
    const state = this.getState();
    return state !== null && key in state;
  }

  // Odczytywanie konkretnego klucza z typowaniem
  getStateValue(key: string): unknown {
    const state = this.getState();
    return state?.[key] || null;
  }
}
