import { Routes } from '@angular/router';
import { TotpVerifyComponent } from '@features/totp/components/totp-verify/totp-verify.component';

export const TOTP_ROUTES: Routes = [
  {
    path: 'totp',
    children: [
      {
        path: 'verify',
        component: TotpVerifyComponent,
      },
    ],
  },
];
