import { Component, Output, EventEmitter } from '@angular/core';
import { TranslateService, TOTPService, ErrorService, LoggingService } from '@core/services';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-totp-verify',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './totp-verify.component.html',
  styleUrls: ['./totp-verify.component.css'],
})
export class TotpVerifyComponent {
  @Output() verificationComplete = new EventEmitter<boolean>(false);

  verificationCode: string = '';
  verificationSuccess: string | null = null;
  isVerifying: boolean = false;

  constructor(
    private translateService: TranslateService,
    private totpService: TOTPService,
    private errorService: ErrorService,
    private logService: LoggingService
  ) {}

  verifyCode(): void {
    if (!this.verificationCode || this.verificationCode.length !== 6) {
      this.errorService.setFieldError('code', this.translateService.translateFunction('ERROR.TOTP.INVALID_CODE'));
      return;
    }

    this.totpService.verify({ code: this.verificationCode }).subscribe({
      next: (response) => {
        this.isVerifying = true;
        this.verificationComplete.emit(true);
        this.verificationSuccess = this.translateService.translateFunction('SUCCESS.TOTP.VERIFICATION_SUCCESS');
        this.logService.info('TOTP verification successful', { response });
      },
      error: (error) => {
        this.isVerifying = false;
        this.errorService.setFieldError(
          'code',
          this.translateService.translateFunction('ERROR.TOTP.VERIFICATION_FAILED')
        );
        this.verificationComplete.emit(false);
        this.logService.error('TOTP verification failed', { error });
      },
    });
  }

  get codeError(): string | null {
    return this.errorService.getFieldError('code');
  }

  onCodeInput(): void {
    this.errorService.clearFieldError('code');
    // Auto-submit when 6 digits are entered
    if (this.verificationCode.length === 6) {
      this.verifyCode();
    }
  }
}
