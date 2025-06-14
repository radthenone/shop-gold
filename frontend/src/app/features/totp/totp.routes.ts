import { Routes } from '@angular/router';
import { TotpVerifyComponent, TotpStatusComponent, TotpSetupComponent } from '@features/totp/components';

export const TOTP_ROUTES: Routes = [
  {
    path: 'verify',
    component: TotpVerifyComponent,
  },
  {
    path: 'status',
    component: TotpStatusComponent,
  },
  {
    path: 'setup',
    component: TotpSetupComponent,
  },
];
