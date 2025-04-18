import { Component, OnInit } from '@angular/core';
import { TOTPService } from '../../../core/services/totp.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-totp-setup',
  templateUrl: './totp-setup.component.html',
  styleUrls: ['./totp-setup.component.scss']
})
export class TOTPSetupComponent implements OnInit {
  qrCode: SafeHtml | null = null;
  error: string | null = null;
  isEnabled = false;
  verificationCode = '';
  isLoading = false;
  recoveryCodes: string[] | null = null;

  constructor(
    private totpService: TOTPService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.checkStatus();
  }

  checkStatus(): void {
    this.isLoading = true;
    this.error = null;

    this.totpService.getStatus().subscribe({
      next: (response) => {
        this.isEnabled = response.is_enabled;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = err.error.detail || 'Błąd podczas sprawdzania statusu 2FA';
        this.isLoading = false;
      }
    });
  }

  setupTOTP(): void {
    this.isLoading = true;
    this.error = null;

    this.totpService.setup().subscribe({
      next: (response) => {
        if (!response.qr_code_svg) {
          this.error = `Can't generate QR code`;
          return;
        }
        this.qrCode = this.sanitizer.bypassSecurityTrustHtml(response.qr_code_svg);
        this.isLoading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error with 2FA QR code';
        this.isLoading = false;
      }
    });
  }

  activateTOTP(): void {
    const code = this.verificationCode.trim();

    if (!/^\d{6}$/.test(code)) {
      this.error = 'Code must have 6 digits';
      return;
    }

    // Check if code is longer than 30 seconds
    this.isLoading = true;
    this.error = null;

    // Send code to activate TOTP
    this.totpService.activate(code).subscribe({
      next: (response) => {
        this.isEnabled = true;
        this.recoveryCodes = response.recovery_codes || [];
        this.qrCode = null;
        this.verificationCode = '';
        this.isLoading = false;
      },
      error: (err) => {
        this.error = err.error?.error || err.error?.detail || 'Wrong code';
        this.isLoading = false;
        this.verificationCode = '';
      }
    });
  }

  deactivateTOTP(): void {
    if (confirm('Are you sure you want to deactivate 2FA?')) {
      this.isLoading = true;
      this.error = null;

      this.totpService.deactivate().subscribe({
        next: () => {
          this.isEnabled = false;
          this.qrCode = null;
          this.recoveryCodes = null;
          this.isLoading = false;
        },
        error: (err) => {
          this.error = err.error.detail || 'Error with deactivate 2FA';
          this.isLoading = false;
        }
      });
    }
  }
}
