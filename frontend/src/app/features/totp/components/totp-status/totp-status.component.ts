import { Component } from '@angular/core';
import { TOTPService } from '@core/services';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-totp-status',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './totp-status.component.html',
  styleUrls: ['./totp-status.component.css'],
})
export class TotpStatusComponent {
  isEnabled: boolean = false;
  constructor(private totpService: TOTPService) {
    this.checkStatus();
  }

  checkStatus(): void {
    if (this.totpService.isTotpEnabled) {
      this.isEnabled = true;
      console.log('TOTP is enabled.');
    } else {
      console.log('TOTP is disabled.');
    }
  }
}
