import { Component, OnInit, OnDestroy, OnChanges } from '@angular/core';
import { TranslateService } from '@app/core';
import { CommonModule } from '@angular/common';
import { UrlConfigService } from '@core/services/url-config.service';
import { Subscription } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-select-lang',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './select-lang.component.html',
  styleUrls: ['./select-lang.component.css'],
})
export class SelectLangComponent implements OnInit, OnDestroy, OnChanges {
  currentLanguage: string;
  private langSubscription?: Subscription;

  constructor(
    private translate: TranslateService,
    private urlConfigService: UrlConfigService
  ) {
    this.currentLanguage = this.translate.getLanguage();
  }

  ngOnInit(): void {
    // Subscribe to language changes to keep selector in sync
    this.langSubscription = this.urlConfigService.currentLang$.subscribe((lang) => {
      this.currentLanguage = lang;
    });
  }

  ngOnDestroy(): void {
    this.langSubscription?.unsubscribe();
  }

  ngOnChanges(): void {
    this.langSubscription = this.urlConfigService.currentLang$.subscribe((lang) => {
      this.currentLanguage = lang;
    });
  }

  changeLanguage(lang: string): void {
    if (this.currentLanguage !== lang) {
      this.translate.setLanguage(lang);
    }
  }
  onLanguageChange(event: Event): void {
    const lang = (event.target as HTMLSelectElement).value;
    this.changeLanguage(lang);
  }
}
