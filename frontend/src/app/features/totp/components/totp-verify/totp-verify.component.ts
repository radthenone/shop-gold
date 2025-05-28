import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-totp-verify',
  standalone: true,
  imports: [],
  templateUrl: './totp-verify.component.html',
  styleUrls: ['./totp-verify.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TotpVerifyComponent {}
