import { ActivatedRouteSnapshot, RouterStateSnapshot, Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { inject } from '@angular/core';

export const AuthGuard: CanActivateFn = (
  next: ActivatedRouteSnapshot, // eslint-disable-line @typescript-eslint/no-unused-vars
  state: RouterStateSnapshot // eslint-disable-line @typescript-eslint/no-unused-vars
) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    router.navigate(['/auth/login']).then();
    return false;
  }

  return true;
};
