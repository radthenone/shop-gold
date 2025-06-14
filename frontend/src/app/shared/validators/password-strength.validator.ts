import { AbstractControl, ValidationErrors } from '@angular/forms';

export class strongPasswordValidator {
  static readonly MIN_LENGTH = 8;
  static readonly UPPER_CASE_REGEX = /[A-Z]/;
  static readonly LOWER_CASE_REGEX = /[a-z]/;
  static readonly DIGIT_REGEX = /\d/;
  static readonly SPECIAL_CHAR_REGEX = /[@$!%*?&]/;

  static passwordStrength(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const errors: ValidationErrors = {};
    let hasError = false;

    // Validation password length
    if (value.length < strongPasswordValidator.MIN_LENGTH) {
      errors['minLength'] = {
        requiredLength: strongPasswordValidator.MIN_LENGTH,
        actualLength: value.length,
      };
      hasError = true;
    }

    // Validation password uppercase
    if (!strongPasswordValidator.UPPER_CASE_REGEX.test(value)) {
      errors['upperCase'] = true;
      hasError = true;
    }

    // Validation password lowercase
    if (!strongPasswordValidator.LOWER_CASE_REGEX.test(value)) {
      errors['lowerCase'] = true;
      hasError = true;
    }

    // Validation password digit
    if (!strongPasswordValidator.DIGIT_REGEX.test(value)) {
      errors['digit'] = true;
      hasError = true;
    }

    // Validation password special character
    if (!strongPasswordValidator.SPECIAL_CHAR_REGEX.test(value)) {
      errors['specialChar'] = true;
      hasError = true;
    }

    return hasError ? errors : null;
  }
}
