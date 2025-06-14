import { CommonModule } from '@angular/common';
import { Component, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ErrorService, LoggingService, TOTPService, TranslateService } from '@app/core';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-totp-activate',
  standalone: true,
  imports: [CommonModule, TranslateModule, FormsModule],
  templateUrl: './totp-activate.component.html',
  styleUrls: ['./totp-activate.component.css'],
})
export class TotpActivateComponent {
  @Output() activationComplete = new EventEmitter<boolean>(false);
  @Output() goBack = new EventEmitter<void>();

  constructor(
    private loggingService: LoggingService,
    private errorService: ErrorService,
    private totpService: TOTPService,
    private translateService: TranslateService
  ) {}

  activateCode: string = '';
  isActivated: boolean = false;
  recoveryCodes: string[] = [];

  setActivated() {
    if (!this.activateCode || this.activateCode.length !== 6) {
      this.errorService.setFieldError('code', this.translateService.translateFunction('ERROR.TOTP.INVALID_CODE'));
      return;
    }

    this.totpService.activate({ code: this.activateCode }).subscribe({
      next: (response) => {
        this.isActivated = response.status;
        this.recoveryCodes = response.recovery_codes || [];
        this.activationComplete.emit();
        this.loggingService.info('TOTP activated successfully', response);
      },
      error: (error) => {
        this.isActivated = false;
        this.errorService.setFieldError('code', error);
        this.loggingService.error('Error activating TOTP', error);
      },
    });
  }

  get codeError(): string | null {
    return this.errorService.getFieldError('code');
  }

  onCodeInput() {
    this.errorService.clearFieldError('code');
  }

  onCodeActivate() {
    this.errorService.clearFieldError('code');
    if (this.activateCode.length === 6) {
      this.setActivated();
    }
  }

  onGoBack() {
    this.goBack.emit();
  }
}
