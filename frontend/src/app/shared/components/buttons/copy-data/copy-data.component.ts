import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TranslateService } from '@core/services';

@Component({
  selector: 'app-copy-data',
  standalone: true,
  imports: [],
  templateUrl: './copy-data.component.html',
  styleUrls: ['./copy-data.component.css'],
})
export class CopyDataComponent {
  @Input() textToCopy!: string;
  @Output() copied = new EventEmitter<string>();

  buttonText: string = this.translateService.translateFunction('BUTTON.COPY');

  constructor(private translateService: TranslateService) {}

  copyText(): void {
    if (!this.textToCopy) return;
    navigator.clipboard.writeText(this.textToCopy).then(
      () => {
        this.copied.emit(this.translateService.translateFunction('BUTTON.COPY_SUCCESS'));
        console.log('Text copied to clipboard');
      },
      (err) => {
        this.copied.emit(this.translateService.translateFunction('BUTTON.COPY_ERROR'));
        console.error('Failed to copy text:', err);
      }
    );
  }
}
