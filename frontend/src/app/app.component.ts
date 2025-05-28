import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainComponent } from '@layout/main/main.component';
import { HeaderComponent } from '@layout/header/header.component';
import { FooterComponent } from '@layout/footer/footer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  styleUrls: ['./app.styles.css'],
  templateUrl: './app.template.html',
  imports: [RouterOutlet, MainComponent, HeaderComponent, FooterComponent],
})
export class AppComponent {}
