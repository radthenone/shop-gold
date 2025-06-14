import { Component, OnInit } from '@angular/core';
import { AuthService } from '@core/services';
import { AuthUser } from '@core/interfaces';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { LogoutComponent } from '@features/auth/components/logout/logout.component';
import { BackToComponent } from '@shared/components/buttons';

@Component({
  selector: 'app-account-panel',
  standalone: true,
  imports: [CommonModule, TranslateModule, LogoutComponent, BackToComponent],
  templateUrl: './account-panel.component.html',
  styleUrls: ['./account-panel.component.css'],
})
export class AccountPanelComponent implements OnInit {
  user: AuthUser | null = null;
  isDropdownOpen = false;

  constructor(private AuthService: AuthService) {}

  ngOnInit(): void {
    this.AuthService.user$.subscribe((user) => {
      this.user = user;
    });
  }
  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }
}
