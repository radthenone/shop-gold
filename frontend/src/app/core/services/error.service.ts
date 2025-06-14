import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { LoggingService, TranslateService } from '@core/services';
import { DjangoError, MessageError, FieldError } from '@core/interfaces';
import { strongPasswordValidator } from '@shared/validators/password-strength.validator';

@Injectable({
  providedIn: 'root',
})
export class ErrorService {
  private fieldErrors: { [field: string]: FieldError | null } = {};
  isFormErrorGlobalCreated: boolean = false;
  isFormErrorsCreated: boolean = false;
  serverErrorKeys = ['serverNonFieldErrors', 'serverFieldErrors'];
  constructor(
    private logger: LoggingService,
    private translate: TranslateService
  ) {}

  private getClientMessage(errorType: string, errorValue?: any): MessageError {
    /**
     * Maps server-side error codes to client-friendly messages.
     */
    switch (errorType) {
      case 'required':
        return { message: this.translate.translateFunction('ERROR.FIELD_REQUIRED') };
      case 'email':
        return { message: this.translate.translateFunction('ERROR.INVALID_EMAIL') };
      case 'minlength':
      case 'minLength': {
        return {
          message: this.translate.translateFunction('ERROR.MIN_LENGTH', {
            min: errorValue?.requiredLength || strongPasswordValidator.MIN_LENGTH,
          }),
        };
      }
      case 'maxlength':
      case 'maxLength':
        return {
          message: this.translate.translateFunction('ERROR.MAX_LENGTH', {
            max: errorValue?.requiredLength || '20',
          }),
        };
      case 'pattern':
        return { message: this.translate.translateFunction('ERROR.PATTERN_MISMATCH') };
      case 'passwordMismatch':
        return { message: this.translate.translateFunction('ERROR.PASSWORD_MISMATCH') };
      case 'passwordsDontMatch':
        return { message: this.translate.translateFunction('ERROR.PASSWORDS_DONT_MATCH') };
      case 'upperCase':
        return { message: this.translate.translateFunction('ERROR.UPPERCASE_REQUIRED') };
      case 'lowerCase':
        return { message: this.translate.translateFunction('ERROR.LOWERCASE_REQUIRED') };
      case 'digit':
        return { message: this.translate.translateFunction('ERROR.NUMBER_REQUIRED') };
      case 'specialChar':
        return { message: this.translate.translateFunction('ERROR.SPECIAL_CHAR_REQUIRED') };
      default:
        this.logger.warn(`Unrecognized client error type: ${errorType}`);
        return { message: this.translate.translateFunction('ERROR.VALIDATION', { error: errorType }) };
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
      this.logger.debug(`getAllErrorsForField: Client errors for field '${fieldName}':`, clientErrors);
      return clientErrors;
    }

    const serverFieldErrors = errors['serverFieldErrors'];
    if (serverFieldErrors && Array.isArray(serverFieldErrors) && serverFieldErrors.length > 0) {
      this.logger.debug(`getAllErrorsForField: Server errors for field '${fieldName}':`, serverFieldErrors);
      return serverFieldErrors as FieldError[];
    }

    this.logger.warn(`getAllErrorsForField: Not found '${fieldName}'.`);
    return null;
  }

  setDjangoErrors(error: HttpErrorResponse): DjangoError | null {
    /**
     * Converts the error response from the server to the DjangoError object.
     * Supports various formats of answers from DRF.
     */
    if (!error || !error.error) {
      this.logger.error('setDjangoErrors: Wrong error format or no error provided.', error);
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
      'errors' in error.error &&
      Array.isArray(error.error.errors)
    ) {
      return { non_field_errors: error.error.errors };
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

    const fieldErrors: FieldError[] = nonFieldErrorsMessages.map((msg: string) => ({
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
          const fieldErrors: FieldError[] = messages.map((msg: string) => ({
            value: true,
            message: msg,
            errorType: 'serverFieldError',
          }));
          control.setErrors({ ...control.errors, serverFieldErrors: fieldErrors }, { emitEvent: false });
          control.markAsTouched();
        }
      } else {
        this.logger.warn(`getServerFieldErrors: Not found control '${field}' in form.`);
      }
    });
  }

  handleError(error: HttpErrorResponse, fieldName?: string): string | null {
    /**
     *Processes http error.
     *If `Fieldname` is given, he returns the first mistake for this particular field.
     *If `Fieldname" is not given, the first error encountered 'non_field_errors' returns.
     *If there is no `Non_field_errors`, the first mistake for any field returns.
     *Otherwise he returns Null.
     */

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
    // this.logger.logHttpError(error, 'FormError');

    const djangoError = this.setDjangoErrors(error);

    if (!djangoError) {
      this.logger.warn('handleServerErrors: djangoError is null, cannot set server errors.');
      return;
    }

    this.getServerNonFieldErrors(form, djangoError);
    this.getServerFieldErrors(form, djangoError);

    this.logFormState(form);
  }

  setFieldError(fieldName: string, error: string | HttpErrorResponse | null): void {
    /**
     * Sets a field error for a specific field in the form.
     * If the error is an instance of HttpErrorResponse, it processes the error and sets the appropriate message.
     * If the error is null, it clears the field error.
     */
    if (!fieldName) return;

    if (typeof error === 'string') {
      this.fieldErrors[fieldName] = {
        value: true,
        message: error,
        errorType: 'clientFieldError',
      };
      return;
    }

    if (error instanceof HttpErrorResponse) {
      const errorMessage = this.handleError(error, fieldName);
      if (errorMessage) {
        this.fieldErrors[fieldName] = {
          value: true,
          message: errorMessage,
          errorType: 'serverFieldError',
        };
      } else {
        this.fieldErrors[fieldName] = null;
      }
      return;
    }

    if (error === null) {
      this.fieldErrors[fieldName] = null;
    }
  }

  getFieldError(fieldName: string): string | null {
    /**
     * Returns the field error for a specific field.
     * If no error is set for the field, it returns null.
     */
    return this.fieldErrors[fieldName]?.message || null;
  }

  clearFieldError(fieldName: string): void {
    /**
     * Clears the field error for a specific field.
     * This is useful when the error is resolved and no longer needs to be displayed.
     */
    if (fieldName) {
      this.fieldErrors[fieldName] = null;
    }
  }

  private logFormState(form: FormGroup): void {
    /**
     * Loguje stan formularza dla celów debugowania.
     */
    this.logger.debug('Form error status:', {
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
