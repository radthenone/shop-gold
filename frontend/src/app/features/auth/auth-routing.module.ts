import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { TOTPVerifyComponent } from './totp-verify/totp-verify.component';
import { RecoveryCodeComponent } from './recovery-code/recovery-code.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'totp-verify', component: TOTPVerifyComponent },
  { path: 'recovery-code', component: RecoveryCodeComponent },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AuthRoutingModule {}
