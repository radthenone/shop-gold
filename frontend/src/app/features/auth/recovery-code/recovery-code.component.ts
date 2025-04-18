import { Component, OnInit } from '@angular/core';
import { TOTPService } from '../../../core/services/totp.service';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-recovery-code',
  templateUrl: './recovery-code.component.html',
  styleUrls: ['./recovery-code.component.scss'],
})
export class RecoveryCodeComponent implements OnInit {
  recoveryCode = '';
  error: string | null = null;
  isLoading = false;
  isMFALogin = false;

  constructor(
    private totpService: TOTPService,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Check if this is MFA during login
    this.isMFALogin = !localStorage.getItem('access_token') &&
                      !!sessionStorage.getItem('temp_login_data');

    // If no temp login data and not logged in, redirect to login
    if (!this.isMFALogin && !this.authService.isLoggedIn()) {
      this.router.navigate(['/auth/login']);
    }
  }

  verifyRecoveryCode(): void {
    if (!this.recoveryCode.trim()) {
      this.error = 'Kod odzyskiwania jest wymagany';
      return;
    }

    this.isLoading = true;
    this.error = null;

    this.totpService.verifyRecoveryCode(this.recoveryCode).subscribe({
      next: (response) => {
        this.isLoading = false;

        // Check if we received tokens (MFA login case)
        if (response.access && response.refresh) {
          // Complete login with tokens
          this.authService.completeLoginAfterMFA(response);
        } else {
          // Regular recovery code verification (already logged in)
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
          this.error = err.error?.detail || err.error?.error || 'Nieprawidłowy kod odzyskiwania';
        }
      },
    });
  }

  backToTOTP(): void {
    this.router.navigate(['/auth/totp-verify']);
  }
}
