import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AuthRoutingModule } from './auth-routing.module';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { TOTPVerifyComponent } from './totp-verify/totp-verify.component';
import { RecoveryCodeComponent } from './recovery-code/recovery-code.component';

@NgModule({
  declarations: [
    LoginComponent,
    RegisterComponent,
    TOTPVerifyComponent,
    RecoveryCodeComponent,
  ],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, AuthRoutingModule],
})
export class AuthModule {}
