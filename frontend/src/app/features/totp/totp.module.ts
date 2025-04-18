import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TOTPRoutingModule } from './totp-routing.module';
import { TOTPSetupComponent } from './setup/totp-setup.component';

@NgModule({
  declarations: [
    TOTPSetupComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    TOTPRoutingModule
  ]
})
export class TOTPModule { }
