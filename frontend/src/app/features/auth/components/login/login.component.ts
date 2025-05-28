import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '@core/services/auth.service';
import { Router } from '@angular/router';
import { strongPasswordValidator } from '@shared/validators/password-strength.validator';
import { AbstractControl } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { LoggingService } from '../../../../core/services/logging.service';
import { ErrorService } from '../../../../core/services/error.service';
import { FieldError } from '@core/models/error.model';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [ReactiveFormsModule, CommonModule],
})
export class LoginComponent implements OnInit, OnDestroy {
  loginForm!: FormGroup;
  submitted = false;
  registrationMessage: string | null = null;
  private authSubscription: Subscription | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private loggingService: LoggingService,
    private errorService: ErrorService
  ) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state && navigation?.extras.state['registerMessage']) {
      this.registrationMessage = navigation.extras.state['registerMessage'] as string;
    }
  }

  ngOnInit() {
    this.loginForm = this.fb.group({
      email: ['adam@adam.com', [Validators.required, Validators.email]],
      password: ['Password12345!', [Validators.required, strongPasswordValidator.passwordStrength]],
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  get field(): { [key: string]: AbstractControl<any, any> } {
    return this.loginForm.controls;
  }

  getFieldErrors(fieldName: string): FieldError[] | null {
    if (!this.submitted) {
      return null;
    }
    return this.errorService.getAllErrorsForField(this.loginForm, fieldName);
  }

  getFormErrors(): FieldError[] | null {
    if (!this.submitted) {
      return null;
    }
    return this.errorService.getAllNonFieldErrors(this.loginForm);
  }

  onSubmit() {
    this.submitted = true;

    if (this.loginForm.invalid) {
      return;
    }

    this.authSubscription?.unsubscribe();

    this.authSubscription = this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        if ('access' in response && 'refresh' in response) {
          setTimeout(() => {
            this.router.navigate(['/']).then();
          }, 1000);
        } else if ('mfa_required' in response) {
          setTimeout(() => {
            this.router.navigate(['/totp/verify/']).then();
          }, 1000);
        }
      },
      error: (error) => {
        this.errorService.handleServerErrors(this.loginForm, error);
      },
    });
  }

  ngOnDestroy(): void {
    this.authSubscription?.unsubscribe();
  }
}
