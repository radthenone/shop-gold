import { ActivatedRouteSnapshot, RouterStateSnapshot, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { NavigationService } from '../services/navigation.service';
import { inject } from '@angular/core';

export const AuthGuard: CanActivateFn = (
  next: ActivatedRouteSnapshot, // eslint-disable-line @typescript-eslint/no-unused-vars
  state: RouterStateSnapshot // eslint-disable-line @typescript-eslint/no-unused-vars
) => {
  const authService = inject(AuthService);
  const navigationService = inject(NavigationService);

  if (!authService.isLoggedIn()) {
    navigationService.navigateWithLang(['auth', 'login']).then();
    return false;
  }

  return true;
};
