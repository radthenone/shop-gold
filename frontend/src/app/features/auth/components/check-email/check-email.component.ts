import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService, ErrorService, TranslateService } from '@core/services';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { TranslateModule } from '@ngx-translate/core';
import { BackToComponent } from '@shared/components/buttons';

@Component({
  selector: 'app-check-email',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule, BackToComponent],
  templateUrl: './check-email.component.html',
  styleUrls: ['./check-email.component.css'],
})
export class CheckEmailComponent {
  email: string = '';
  emailSuccess: string | null = null;
  emailError: string | null = null;
  submitted: boolean = false;

  constructor(
    private authService: AuthService,
    private errorService: ErrorService,
    private translate: TranslateService
  ) {}

  onCheckEmailSubmit() {
    this.submitted = true;
    this.emailSuccess = null;
    this.emailError = null;

    if (!this.email.trim()) {
      this.emailError = this.translate.translateFunction('ERROR.INVALID_EMAIL');
      return;
    }

    const emailPattern = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$/;
    if (!emailPattern.test(this.email)) {
      this.emailError = this.translate.translateFunction('ERROR.INVALID_EMAIL_FORMAT');
      return;
    }

    this.authService.checkEmail(this.email).subscribe({
      next: (response) => {
        this.emailSuccess = response.detail || this.translate.translateFunction('SUCCESS.CHECK_EMAIL');
      },
      error: (error: HttpErrorResponse) => {
        this.emailError =
          this.errorService.handleError(error, 'email') || this.translate.translateFunction('ERROR.GENERIC');
      },
    });
  }
}
