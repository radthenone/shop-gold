import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule],
})
export class HomeComponent {
  verifyMessage: string | null = null;
  errorVerifyMessage: string | null = null;

  constructor(private router: Router) {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state && navigation?.extras.state['verifyMessage']) {
      this.verifyMessage = navigation.extras.state['verifyMessage'] as string;
    } else {
      this.verifyMessage = null;
    }

    if (navigation?.extras.state && navigation?.extras.state['errorVerifyMessage']) {
      this.errorVerifyMessage = navigation.extras.state['errorVerifyMessage'] as string;
    } else {
      this.errorVerifyMessage = null;
    }
  }
}
