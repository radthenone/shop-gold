import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { TOTPService } from '../../../core/services/totp.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-totp-verify',
  templateUrl: './totp-verify.component.html',
  styleUrls: ['./totp-verify.component.scss'],
})
export class TOTPVerifyComponent {
  verifyForm: FormGroup;
  error: string | null = null;
  isLoading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private totpService: TOTPService,
    private authService: AuthService,
    private router: Router
  ) {
    this.verifyForm = this.fb.group({
      code: ['', [Validators.required, Validators.pattern('^[0-9]{6}$')]],
    });

    // Sprawdź czy są tymczasowe dane logowania
    if (!sessionStorage.getItem('temp_login_data')) {
      this.router.navigate(['/auth/login']);
    }
  }

  onSubmit(): void {
    if (this.verifyForm.valid) {
      this.error = null;
      this.isLoading = true;
      const { code } = this.verifyForm.value;

      this.totpService.verify(code).subscribe({
        next: (response) => {
          this.isLoading = false;

          // Check if we received tokens (MFA login case)
          if (response.access && response.refresh) {
            // Complete login with tokens
            this.authService.completeLoginAfterMFA(response);
          } else {
            // Regular TOTP verification (already logged in)
            // Just redirect to home page
            this.router.navigate(['/']);
          }
        },
        error: (err) => {
          this.isLoading = false;
          if (typeof err === 'string') {
            this.error = err;
          } else if (err instanceof Error) {
            this.error = err.message;
          } else {
            this.error = err.error?.detail || err.error?.error || 'Nieprawidłowy kod weryfikacyjny';
          }
        },
      });
    }
  }
}
