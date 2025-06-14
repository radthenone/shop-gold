import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { strongPasswordValidator } from '@shared/validators/password-strength.validator';
import { AbstractControl } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { AuthService, LoggingService, ErrorService, NavigationService } from '@core/services';
import { FieldError } from '@core/interfaces';
import { TranslateModule } from '@ngx-translate/core';
import { BackToComponent } from '@shared/components/buttons';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [ReactiveFormsModule, CommonModule, TranslateModule, BackToComponent],
})
export class LoginComponent implements OnInit, OnDestroy {
  loginForm!: FormGroup;
  submitted = false;
  navSuccessMessage: string | null = null;
  private authSubscription: Subscription | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private logService: LoggingService,
    private errorService: ErrorService,
    private navService: NavigationService
  ) {
    if (this.navService.isStateValid('navSuccessMessage')) {
      this.navSuccessMessage = this.navService.getStateValue('navSuccessMessage') as string;
    }
  }

  ngOnInit() {
    this.loginForm = this.fb.group({
      email: ['user@example.com', [Validators.required, Validators.email]],
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
          this.navService.navigateWithLang([]);
          this.logService.info('User logged in successfully', response);
        } else if ('mfa_required' in response) {
          this.navService.navigateWithLang(['totp', 'verify']);
          this.logService.info('MFA required, redirecting to TOTP verification', response);
        }
      },
      error: (error) => {
        this.errorService.handleServerErrors(this.loginForm, error);
        this.logService.error('Login failed', error);
      },
    });
  }

  ngOnDestroy(): void {
    this.authSubscription?.unsubscribe();
  }
}
