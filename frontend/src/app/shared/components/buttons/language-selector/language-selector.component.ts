import { Component } from '@angular/core';
import { TranslateService } from '@core/services/translate.service';

@Component({
  selector: 'app-language-selector',
  standalone: true,
  imports: [],
  templateUrl: './language-selector.component.html',
  styleUrls: ['./language-selector.component.css'],
})
export class LanguageSelectorComponent {
  public currentLanguage: string;

  constructor(private translateService: TranslateService) {
    this.currentLanguage = this.translateService.getLanguage();
  }

  changeLanguage(lang: string): void {
    this.translateService.setLanguage(lang);
    this.currentLanguage = lang;
  }

  onLanguageChange(event: Event): void {
    const lang = (event.target as HTMLSelectElement).value;
    this.changeLanguage(lang);
  }
}
