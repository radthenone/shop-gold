import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  loginForm: FormGroup;
  error: string | null = null;
  isLoading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.error = null;
      this.isLoading = true;
      const { email, password } = this.loginForm.value;

      this.authService.login(email, password).subscribe({
        next: (response) => {
          this.isLoading = false;

          // If user has MFA enabled, redirect to TOTP verification
          if (response.mfa_required) {
            // Store email in session storage for MFA verification
            sessionStorage.setItem(
              'temp_login_data',
              JSON.stringify({ email })
            );
            this.router.navigate(['/auth/totp-verify']);
          } else {
            // If no MFA, set tokens and redirect to home page
            this.authService.completeLoginAfterMFA(response);
          }
        },
        error: (err) => {
          this.isLoading = false;
          if (typeof err === 'string') {
            this.error = err;
          } else if (err instanceof Error) {
            this.error = err.message;
          } else {
            this.error = err.error?.detail || err.error?.message || 'Błąd logowania';
          }
        },
      });
    } else {
      // Mark all fields as touched to show validation messages
      Object.keys(this.loginForm.controls).forEach((key) => {
        const control = this.loginForm.get(key);
        control?.markAsTouched();
      });
    }
  }
}
