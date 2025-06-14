import { Component } from '@angular/core';
import { SelectLangComponent, AccountPanelComponent } from '@app/shared/components';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
  standalone: true,
  imports: [SelectLangComponent, AccountPanelComponent],
})
export class NavbarComponent {}
