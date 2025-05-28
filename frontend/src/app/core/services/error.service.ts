import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { LoggingService } from '@core/services/logging.service';
import { DjangoError, MessageError, FieldError } from '@core/models/error.model';

@Injectable({
  providedIn: 'root',
})
export class ErrorService {
  isFormErrorGlobalCreated: boolean = false;
  isFormErrorsCreated: boolean = false;
  serverErrorKeys = ['serverNonFieldErrors', 'serverFieldErrors'];

  constructor(private logger: LoggingService) {}

  private getClientMessage(errorType: string, errorValue?: any): MessageError {
    /**
     * Maps server-side error codes to client-friendly messages.
     */
    switch (errorType) {
      case 'required':
        return { message: 'This field is required.' };
      case 'email':
        return { message: 'Please enter a valid email address.' };
      case 'minlength':
        return { message: `Minimum length is ${errorValue?.requiredLength} characters.` };
      case 'maxlength':
        return { message: `Maximum length is ${errorValue?.requiredLength} characters.` };
      case 'pattern':
        return { message: 'Value does not match the required pattern.' };
      case 'passwordMismatch':
        return { message: 'Passwords do not match.' };
      case 'passwordsDontMatch':
        return { message: 'The provided passwords are not identical.' };
      case 'requiredTrue':
        return { message: 'This field must be checked.' };
      case 'minLength':
        return { message: 'Password is too short.' };
      case 'upperCase':
        return { message: 'Password must contain at least one uppercase letter.' };
      case 'lowerCase':
        return { message: 'Password must contain at least one lowercase letter.' };
      case 'digit':
        return { message: 'Password must contain at least one digit.' };
      case 'specialChar':
        return { message: 'Password must contain at least one special character.' };
      default:
        this.logger.warn(`Unrecognized client error type: ${errorType}`);
        return { message: `Validation error: ${errorType}` };
    }
  }

  getAllNonFieldErrors(form: FormGroup): FieldError[] | null {
    /**
     * Returns all non-field errors from the form.
     * Non-field errors are typically used for validation messages that are not tied to a specific field.
     */
    if (!form) {
      return null;
    }
    const formErrors = form.errors;
    if (formErrors) {
      const serverNonFieldErrors = formErrors['serverNonFieldErrors'] as FieldError[];
      if (serverNonFieldErrors && Array.isArray(serverNonFieldErrors) && serverNonFieldErrors.length > 0) {
        return serverNonFieldErrors;
      }
    }
    return null;
  }

  getAllFormErrors(form: FormGroup, formErrorName: string): FieldError | null {
    /**
     * Returns a specific form error based on the provided error name.
     * This is useful for displaying specific error messages related to the form as a whole.
     */
    if (!form || !formErrorName) {
      return null;
    }

    const formErrors = form.errors;
    if (!formErrors) {
      return null;
    }
    const errorValue = formErrors[formErrorName];

    if (Object.hasOwn(formErrors, formErrorName)) {
      if (errorValue) {
        return {
          value: errorValue,
          message: this.getClientMessage(formErrorName, errorValue).message,
          errorType: formErrorName,
        };
      }
    }
    return null;
  }

  getAllErrorsForField(form: FormGroup, fieldName: string): FieldError[] | null {
    /**
     * Returns all errors for a specific field in the form.
     * This is useful for displaying validation messages related to a specific input field.
     */
    if (!form || !fieldName) {
      this.logger.warn('getAllErrorsForField caused with an incorrect form or field name.');
      return null;
    }

    const control = form.get(fieldName);
    if (!control) {
      this.logger.warn(`getAllErrorsForField: No controls for the field: ${fieldName}`);
      return null;
    }

    const errors = control.errors;

    if (!errors) {
      return null;
    }

    const clientErrors: FieldError[] = [];
    Object.keys(errors).forEach((errorKey) => {
      if (errorKey !== 'serverFieldErrors' && errorKey !== 'serverNonFieldErrors') {
        const errorValue = errors[errorKey];
        const clientMessage = this.getClientMessage(errorKey, errorValue);
        clientErrors.push({
          value: true,
          message: clientMessage.message,
          errorType: errorKey,
        });
      }
    });

    if (clientErrors.length > 0) {
      // this.logger.debug(`getAllErrorsForField: Client errors for field '${fieldName}':`, clientErrors);
      return clientErrors;
    }

    const serverFieldErrors = errors['serverFieldErrors'];
    if (serverFieldErrors && Array.isArray(serverFieldErrors) && serverFieldErrors.length > 0) {
      // this.logger.debug(`getAllErrorsForField: Server errors for field '${fieldName}':`, serverFieldErrors);
      return serverFieldErrors as FieldError[];
    }

    this.logger.warn(
      `getAllErrorsForField: Nie znaleziono aktywnych błędów klienta ani serwera dla pola '${fieldName}'.`
    );
    return null;
  }

  setDjangoErrors(error: HttpErrorResponse): DjangoError | null {
    /**
     * Konwertuje odpowiedź błędu z serwera na obiekt DjangoError.
     * Obsługuje różne formaty odpowiedzi z DRF.
     */
    if (!error || !error.error) {
      this.logger.error('setDjangoErrors: Brak obiektu błędu lub error.error w odpowiedzi HTTP.');
      return null;
    }
    if (typeof error.error === 'string') {
      return { non_field_errors: [error.error] };
    }
    if (
      typeof error.error === 'object' &&
      error.error !== null &&
      'detail' in error.error &&
      typeof error.error.detail === 'string'
    ) {
      return { non_field_errors: [error.error.detail] };
    }
    if (
      typeof error.error === 'object' &&
      error.error !== null &&
      'detail' in error.error &&
      typeof error.error.errors === 'string'
    ) {
      return { non_field_errors: [error.error.errors] };
    }
    if (typeof error.error === 'object' && error.error !== null) {
      return error.error as DjangoError;
    }
    this.logger.warn('setDjangoErrors: Format error.error nie jest rozpoznawany jako DjangoError.', error.error);
    return null;
  }

  getServerNonFieldErrors(form: FormGroup, error: DjangoError): void {
    /**
     * Sets non-field errors from the server response to the form.
     * Non-field errors are typically used for validation messages that are not tied to a specific field.
     */
    if (!error || !error.non_field_errors || error.non_field_errors.length === 0) {
      return;
    }

    const nonFieldErrorsMessages: string[] = error.non_field_errors;

    const fieldErrors: FieldError[] = nonFieldErrorsMessages.map((msg) => ({
      value: true,
      message: msg,
      errorType: 'serverNonFieldError',
    }));

    form.setErrors({ ...form.errors, serverNonFieldErrors: fieldErrors });
    form.markAsTouched();
  }

  getServerFieldErrors(form: FormGroup, error: DjangoError): void {
    /**
     * Sets field-specific errors from the server response to the form.
     * This is useful for displaying validation messages related to specific input fields.
     */
    if (!error) {
      return;
    }
    Object.keys(error).forEach((field) => {
      if (field === 'non_field_errors') {
        return;
      }

      const control = form.get(field);
      if (control) {
        const messages = error[field];
        if (messages && messages.length > 0) {
          const fieldErrors: FieldError[] = messages.map((msg) => ({
            value: true,
            message: msg,
            errorType: 'serverFieldError',
          }));
          control.setErrors({ ...control.errors, serverFieldErrors: fieldErrors }, { emitEvent: false });
          control.markAsTouched();
        }
      } else {
        this.logger.warn(`getServerFieldErrors: Nie znaleziono kontrolki dla pola '${field}' w formularzu.`);
      }
    });
  }

  handleError(error: HttpErrorResponse, fieldName?: string): string | null {
    /**
     * Przetwarza błąd HTTP.
     * Jeśli `fieldName` jest podany, zwraca pierwszy błąd dla tego konkretnego pola.
     * Jeśli `fieldName` nie jest podany, zwraca pierwszy napotkany błąd `non_field_errors`.
     * Jeśli nie ma `non_field_errors`, zwraca pierwszy napotkany błąd dla dowolnego pola.
     * W przeciwnym razie zwraca null.
     */
    // console.log('Original HTTP Error:', error); // Komentarz: Oryginalny błąd HTTP

    if (!error) {
      return null;
    }

    const djangoError = this.setDjangoErrors(error);

    if (!djangoError) {
      this.logger.warn('handleError: djangoError is null, cannot process error.');
      return null;
    }

    if (fieldName) {
      const specificFieldErrors = djangoError[fieldName];
      if (
        Array.isArray(specificFieldErrors) &&
        specificFieldErrors.length > 0 &&
        typeof specificFieldErrors[0] === 'string'
      ) {
        return specificFieldErrors[0];
      }
      return null;
    }

    if (djangoError.non_field_errors && djangoError.non_field_errors.length > 0) {
      return djangoError.non_field_errors[0];
    }

    const fieldErrorKeys = Object.keys(djangoError).filter((key) => key !== 'non_field_errors');
    if (fieldErrorKeys.length > 0) {
      for (const fieldKey of fieldErrorKeys) {
        const fieldErrors = djangoError[fieldKey];
        if (Array.isArray(fieldErrors) && fieldErrors.length > 0 && typeof fieldErrors[0] === 'string') {
          return fieldErrors[0];
        }
      }
    }

    this.logger.warn('handleError: No specific errors found in djangoError to return.', djangoError);
    return null;
  }

  handleServerErrors(form: FormGroup, error: HttpErrorResponse): void {
    /**
     * Handles server errors by setting them in the form.
     * This is useful for displaying validation messages related to server-side validation.
     */
    this.logger.logHttpError(error, 'FormError');

    const djangoError = this.setDjangoErrors(error);

    this.logger.info('Otrzymane błędy serwera (po przetworzeniu):', djangoError);

    if (!djangoError) {
      this.logger.warn('handleServerErrors: djangoError jest null, nie można ustawić błędów serwera.');
      return;
    }

    this.getServerNonFieldErrors(form, djangoError);
    this.getServerFieldErrors(form, djangoError);

    this.logFormState(form);
  }

  private logFormState(form: FormGroup): void {
    /**
     * Loguje stan formularza dla celów debugowania.
     * TODO: Rozważyć ograniczenie logowania w środowisku produkcyjnym.
     */
    this.logger.debug('Stan formularza:', {
      valid: form.valid,
      invalid: form.invalid,
      touched: form.touched,
      dirty: form.dirty,
      errors: form.errors,
      controls: Object.keys(form.controls).map((key) => {
        const control = form.get(key);
        return {
          field: key,
          value: control?.value,
          errors: control?.errors,
          touched: control?.touched,
          valid: control?.valid,
          status: control?.status,
        };
      }),
    });
  }
}
