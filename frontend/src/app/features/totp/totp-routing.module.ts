import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TOTPSetupComponent } from './setup/totp-setup.component';
import { AuthGuard } from '../../core/guards/auth.guard';

const routes: Routes = [
  { 
    path: 'setup', 
    component: TOTPSetupComponent,
    canActivate: [AuthGuard]
  },
  { path: '', redirectTo: 'setup', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TOTPRoutingModule { }
