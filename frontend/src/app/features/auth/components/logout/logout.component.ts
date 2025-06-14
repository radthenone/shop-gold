import { Component } from '@angular/core';
import { AuthService } from '../../../../core/services/auth.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-logout',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
})
export class LogoutComponent {
  constructor(private AuthService: AuthService) {}

  logout() {
    this.AuthService.logout();
  }
}
