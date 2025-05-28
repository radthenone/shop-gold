import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export const passwordMatchValidator = (password: string, confirmPassword: string): ValidatorFn => {
  return (control: AbstractControl): ValidationErrors | null => {
    const passwordControl = control.get(password);
    const confirmControl = control.get(confirmPassword);

    if (passwordControl && confirmControl) {
      return passwordControl.value !== confirmControl.value ? { passwordsDontMatch: true } : null;
    }

    return null;
  };
};
