import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

@Injectable({
  providedIn: 'root',
})
export class LoggingService {
  private currentLogLevel: LogLevel = environment.production ? LogLevel.ERROR : LogLevel.DEBUG;

  constructor() {}

  debug(message: string, ...data: any[]): void {
    this.log(LogLevel.DEBUG, message, ...data);
  }

  info(message: string, ...data: any[]): void {
    this.log(LogLevel.INFO, message, ...data);
  }

  warn(message: string, ...data: any[]): void {
    this.log(LogLevel.WARN, message, ...data);
  }

  error(message: string, ...data: any[]): void {
    this.log(LogLevel.ERROR, message, ...data);
  }

  // Logues the HTTP error structure in a clear way
  logHttpError(error: any, context: string = ''): void {
    const prefix = context ? `[${context}] ` : '';

    this.error(`${prefix}Błąd HTTP:`, {
      status: error.status,
      statusText: error.statusText,
      url: error.url,
      error: error.error,
      message: error.message,
    });

    // If we have a detailed error structure in response
    if (error.error && typeof error.error === 'object') {
      Object.keys(error.error).forEach((field) => {
        this.debug(`${prefix}Błąd dla pola ${field}:`, error.error[field]);
      });
    }
  }

  // Private method for actually logging in
  private log(level: LogLevel, message: string, ...data: any[]): void {
    if (level < this.currentLogLevel) {
      return;
    }

    switch (level) {
      case LogLevel.DEBUG:
        if (data.length > 0) {
          console.debug(message, ...data);
        } else {
          console.debug(message);
        }
        break;
      case LogLevel.INFO:
        if (data.length > 0) {
          console.info(message, ...data);
        } else {
          console.info(message);
        }
        break;
      case LogLevel.WARN:
        if (data.length > 0) {
          console.warn(message, ...data);
        } else {
          console.warn(message);
        }
        break;
      case LogLevel.ERROR:
        if (data.length > 0) {
          console.error(message, ...data);
        } else {
          console.error(message);
        }
        break;
    }
  }
}
