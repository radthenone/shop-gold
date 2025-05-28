import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { LogoutComponent } from './components/logout/logout.component';
import { VerifyEmailComponent } from '@features/auth/components/verify-email/verify-email.component';
import { CheckEmailComponent } from './components/check-email/check-email.component';

export const AUTH_ROUTES: Routes = [
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'register',
    component: RegisterComponent,
  },
  {
    path: 'logout',
    component: LogoutComponent,
  },
  {
    path: 'verify-email/:key',
    component: VerifyEmailComponent,
  },
  {
    path: 'check-email',
    component: CheckEmailComponent,
  },
];
