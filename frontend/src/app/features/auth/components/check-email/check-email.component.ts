import { Component } from '@angular/core';
import { AuthService } from '../../../../core/services/auth.service';
import { CommonModule } from '@angular/common';
import { ErrorService } from '../../../../core/services/error.service';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-check-email',
  standalone: true,
  imports: [CommonModule, FormsModule],
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
    private errorService: ErrorService
  ) {}

  onCheckEmailSubmit() {
    this.submitted = true;
    this.emailSuccess = null;
    this.emailError = null;

    if (!this.email.trim()) {
      this.emailError = 'Please enter an email address.';
      return;
    }

    const emailPattern = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$/;
    if (!emailPattern.test(this.email)) {
      this.emailError = 'Please enter the correct e-mail address.';
      return;
    }

    this.authService.checkEmail(this.email).subscribe({
      next: (response) => {
        console.log('Email check successful:', response);
        this.emailSuccess = response.detail || 'Email check was successful.';
      },
      error: (error: HttpErrorResponse) => {
        this.emailError =
          this.errorService.handleError(error, 'email') || 'An error occurred while checking the email.';
      },
    });
  }
}
