import { Component, OnInit } from '@angular/core';
import { AuthService } from '@app/core/services/auth.service';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  template: `<p>Email verification in progress ...</p>`,
})
export class VerifyEmailComponent implements OnInit {
  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const key = this.route.snapshot.paramMap.get('key');
    if (key) {
      this.verifyEmail(key);
    } else {
      this.router
        .navigate(['/'], { state: { errorverifyMessage: 'No verification key in URL. Contact technical help.' } })
        .then();
    }
  }

  verifyEmail(key: string): void {
    this.authService.verifyEmail(key).subscribe({
      next: (response: { detail: string }) => {
        const successMessage = response.detail || 'Email verified successfully.';
        this.router
          .navigate(['/auth/login'], {
            state: {
              verifyMessage: successMessage,
            },
          })
          .then();
      },
      error: (error: HttpErrorResponse) => {
        const errorMessage = error?.error?.detail || 'An error occurred while verifying the email. Please try again.';
        this.router.navigate(['/'], { state: { errorverifyMessage: errorMessage } }).then();
      },
    });
  }
}
