import { Component, Input } from '@angular/core';
import { NavigationService } from '@core/services';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-back-to',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './back-to.component.html',
  styleUrls: ['./back-to.component.css'],
})
export class BackToComponent {
  @Input() label: string = '';
  @Input() route: string[] = [];
  @Input() state: { [key: string]: any } | null = null;

  constructor(private navigationService: NavigationService) {}

  onBackToLogin() {
    if (this.state) {
      this.navigationService.setStateWithLang(this.route, this.state);
    }
    this.navigationService.navigateWithLang(this.route);
  }
}
