import { CommonModule } from '@angular/common';
import { Component, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { LoggingService, TOTPService } from '@app/core';
import { TranslateModule } from '@ngx-translate/core';
import { CopyDataComponent } from '@shared/components/buttons';

@Component({
  selector: 'app-totp-setup',
  standalone: true,
  imports: [CommonModule, FormsModule, CopyDataComponent, TranslateModule],
  templateUrl: './totp-setup.component.html',
  styleUrls: ['./totp-setup.component.css'],
})
export class TotpSetupComponent {
  @Output() setupComplete = new EventEmitter<{ secret: string }>();

  data: { secret: string; qrCode?: SafeHtml } | null = null;
  copiedMessage?: string;
  isLoading: boolean = true;

  constructor(
    private loggingService: LoggingService,
    private totpService: TOTPService,
    private sanitizer: DomSanitizer
  ) {
    this.getSetupData();
  }

  getSetupData(): void {
    this.isLoading = true;
    this.totpService.setup().subscribe({
      next: (data) => {
        let modifiedQrCode = data.qr_code;
        if (modifiedQrCode) {
          modifiedQrCode = modifiedQrCode.replace(/width="[^"]*"/g, '').replace(/height="[^"]*"/g, '');
        }

        this.data = {
          secret: data.secret,
          qrCode: this.sanitizer.bypassSecurityTrustHtml(modifiedQrCode),
        };
        this.isLoading = false;
        this.loggingService.debug('TOTP setup data received', data);
      },
      error: (error) => {
        this.data = null;
        this.isLoading = false;
        this.loggingService.error('Error during TOTP setup', error);
      },
    });
  }

  onCopied(message: string): void {
    this.copiedMessage = message;
  }

  proceedToVerification(): void {
    if (this.data?.secret) {
      this.setupComplete.emit({ secret: this.data.secret });
    }
  }
}
