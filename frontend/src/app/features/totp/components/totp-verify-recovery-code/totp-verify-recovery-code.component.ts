import { Component, Output, EventEmitter } from '@angular/core';
import { TranslateService, LoggingService, TOTPService, ErrorService } from '@app/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-totp-verify-recovery-code',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './totp-verify-recovery-code.component.html',
  styleUrls: ['./totp-verify-recovery-code.component.css'],
})
export class TotpVerifyRecoveryCodeComponent {
  recoveryCode: string = '';
  isVerifying: boolean = false;
  @Output() recoveryCodeVerified = new EventEmitter<boolean>(false);

  constructor(
    private translateService: TranslateService,
    private loggingService: LoggingService,
    private totpService: TOTPService,
    private errorService: ErrorService
  ) {}

  verifyRecoveryCode() {
    if (!this.recoveryCode || this.recoveryCode.length !== 6) {
      this.errorService.setFieldError('code', this.translateService.translateFunction('ERROR.TOTP.INVALID_CODE'));
      return;
    }

    this.totpService.verifyRecoveryCode({ code: this.recoveryCode }).subscribe({
      next: (response) => {
        this.isVerifying = true;
        this.recoveryCodeVerified.emit(true);
        this.loggingService.info('Recovery code verified successfully', response);
      },
      error: (error) => {
        this.errorService.setFieldError('code', error);
      },
    });
  }

  get codeError(): string | null {
    return this.errorService.getFieldError('code');
  }
}
