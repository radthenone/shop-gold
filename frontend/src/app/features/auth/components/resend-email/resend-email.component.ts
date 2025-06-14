import { Component } from '@angular/core';
import { AuthService, NavigationService, ErrorService, TranslateService } from '@core/services';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { TranslateModule } from '@ngx-translate/core';
import { BackToComponent } from '@shared/components/buttons';

@Component({
  selector: 'app-resend-email',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule, BackToComponent],
  templateUrl: './resend-email.component.html',
  styleUrls: ['./resend-email.component.css'],
})
export class ResendEmailComponent {
  email: string = '';
  isLoading: boolean = false;
  submitted: boolean = false;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private authService: AuthService,
    private errorService: ErrorService,
    private navService: NavigationService,
    private translate: TranslateService
  ) {}

  private isValidEmail(email: string): boolean {
    if (!email || !email.trim()) return false;
    const emailPattern = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$/;
    return emailPattern.test(email.toLowerCase());
  }

  isEmailInvalid(): boolean {
    if (!this.submitted) return false;
    return !this.isValidEmail(this.email);
  }

  onSubmit(): void {
    this.submitted = true;
    this.successMessage = null;
    this.errorMessage = null;

    // Email validation
    if (!this.isValidEmail(this.email)) {
      if (!this.email || !this.email.trim()) {
        this.errorMessage = this.translate.translateFunction('ERROR.FIELD_REQUIRED');
      } else {
        this.errorMessage = this.translate.translateFunction('ERROR.INVALID_EMAIL');
      }
      return;
    }

    this.isLoading = true;

    this.authService.resendEmail(this.email).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = response.detail || this.translate.translateFunction('SUCCESS.EMAIL_RESEND');
        this.email = '';
        this.submitted = false;

        this.navService.setStateWithLang(
          ['auth', 'login'],
          {
            navSuccessMessage: this.successMessage,
          },
          3000
        );
      },
      error: (error: HttpErrorResponse) => {
        this.isLoading = false;
        this.errorMessage =
          this.errorService.handleError(error, 'email') || this.translate.translateFunction('ERROR.GENERIC');
      },
    });
  }
}
