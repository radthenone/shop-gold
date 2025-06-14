import { Component, OnInit } from '@angular/core';
import { AuthService, NavigationService, TranslateService } from '@app/core/services';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  template: `<p>{{ loadingMessage }}</p>`,
})
export class VerifyEmailComponent implements OnInit {
  loadingMessage: string = '';
  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private navigationService: NavigationService,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    this.loadingMessage = this.translate.translateFunction('LOADING.EMAIL_IN_PROGRESS');
    const key = this.route.snapshot.paramMap.get('key');
    if (key) {
      this.verifyEmail(key);
    } else {
      const errorMessage = this.translate.translateFunction('ERROR.NO_VERIFICATION_KEY');
      this.navigationService
        .navigateWithLang([''], {
          state: { errorverifyMessage: errorMessage },
        })
        .then();
    }
  }

  verifyEmail(key: string): void {
    this.authService.verifyEmail(key).subscribe({
      next: (response: { detail: string }) => {
        const successMessage = response.detail || this.translate.translateFunction('SUCCESS.EMAIL_VERIFIED');
        this.navigationService
          .navigateWithLang(['auth', 'login'], {
            state: {
              verifyMessage: successMessage,
            },
          })
          .then();
      },
      error: (error: HttpErrorResponse) => {
        const errorMessage = error?.error?.detail || this.translate.translateFunction('ERROR.GENERIC');
        this.navigationService
          .navigateWithLang([''], {
            state: { errorverifyMessage: errorMessage },
          })
          .then();
      },
    });
  }
}
