import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '@core/services/auth.service';
import { Router, RouterLink } from '@angular/router';
import { strongPasswordValidator } from '@shared/validators/password-strength.validator';
import { passwordMatchValidator } from '@shared/validators/passwords-match-validator';
import { RegisterRequest } from '@core/models/auth.model';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorService } from '@core/services/error.service';
import { LoggingService } from '@core/services/logging.service';
import { FieldError } from '@core/models/error.model';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-register',
  standalone: true,
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
  imports: [ReactiveFormsModule, CommonModule, RouterLink],
})
export class RegisterComponent implements OnInit, OnDestroy {
  registerForm!: FormGroup;
  submitted = false;
  private authSubscription: Subscription | null = null;

  constructor(
    private authService: AuthService,
    private registerFormBuilder: FormBuilder,
    private router: Router,
    private errorService: ErrorService,
    private logger: LoggingService
  ) {}

  ngOnInit() {
    this.registerForm = this.registerFormBuilder.group(
      {
        username: [
          '',
          Validators.compose([
            Validators.required,
            Validators.minLength(5),
            Validators.maxLength(20),
            Validators.pattern('^[a-zA-Z0-9_]+$'),
          ]),
        ],
        email: ['', Validators.compose([Validators.required, Validators.email])],
        password: ['', Validators.compose([Validators.required, strongPasswordValidator.passwordStrength])],
        password_confirm: ['', [Validators.required]],
        first_name: ['', []],
        last_name: ['', []],
        termsAndConditions: [false, [Validators.requiredTrue]],
      },
      {
        validators: passwordMatchValidator('password', 'password_confirm'),
      }
    );
  }
  get field(): { [key: string]: AbstractControl<any, any> } {
    return this.registerForm.controls;
  }

  getFormError(formErrorName: string): FieldError | null {
    if (!this.submitted) {
      return null;
    }
    return this.errorService.getAllFormErrors(this.registerForm, formErrorName);
  }

  getGlobalError(): FieldError[] | null {
    if (!this.submitted) {
      return null;
    }
    return this.errorService.getAllNonFieldErrors(this.registerForm);
  }

  getFieldErrors(fieldName: string): FieldError[] | null {
    if (!this.submitted) {
      return null;
    }
    return this.errorService.getAllErrorsForField(this.registerForm, fieldName);
  }

  private transformData(formData: any): RegisterRequest {
    const { password_confirm, ...rest } = formData;

    return {
      ...rest,
      rewrite_password: password_confirm,
    };
  }

  onSubmit() {
    this.submitted = true;

    if (this.registerForm.invalid) {
      return;
    }

    const data = this.transformData(this.registerForm.value);

    this.authSubscription?.unsubscribe();

    this.authSubscription = this.authService.register(data).subscribe({
      next: (response: { detail: string }) => {
        console.log(response);
        this.router
          .navigate(['/auth/login'], {
            state: {
              registerMessage: response.detail,
            },
          })
          .then();
      },
      error: (error: HttpErrorResponse) => {
        this.errorService.handleServerErrors(this.registerForm, error);
      },
    });
  }

  ngOnDestroy() {
    this.authSubscription?.unsubscribe();
  }
}
