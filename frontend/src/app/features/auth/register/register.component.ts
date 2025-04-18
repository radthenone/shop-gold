import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  registerForm: FormGroup;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(5)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      rewrite_password: ['', [Validators.required]],
      first_name: [''],
      last_name: ['']
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password');
    const rewritePassword = control.get('rewrite_password');

    if (password && rewritePassword && password.value !== rewritePassword.value) {
      rewritePassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }

    return null;
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.error = null;
      this.authService.register(this.registerForm.value).subscribe({
        next: (response) => {
          alert(response.detail);
          this.router.navigate(['/auth/login']);
        },
        error: (err) => this.error = err.error.detail || 'Błąd rejestracji'
      });
    } else {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.registerForm.controls).forEach(key => {
        const control = this.registerForm.get(key);
        control?.markAsTouched();
      });

      if (this.registerForm.hasError('passwordMismatch')) {
        this.error = 'Hasła nie są identyczne';
      }
    }
  }
}
