import { Routes } from '@angular/router';

const mainRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('@features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'auth',
    loadComponent: () => import('@layout/auth/auth.component').then((m) => m.AuthComponent),
    children: [
      {
        path: '',
        loadChildren: () => import('@features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
      },
    ],
  },
  {
    path: 'totp',
    loadChildren: () => import('@features/totp/totp.routes').then((m) => m.TOTP_ROUTES),
  },
  {
    path: '404',
    loadComponent: () =>
      import('@shared/components/not-found/page-not-found.component').then((m) => m.PageNotFoundComponent),
  },
  {
    path: '**',
    redirectTo: '404',
  },
];

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/pl',
    pathMatch: 'full',
  },
  {
    path: 'pl',
    children: mainRoutes,
  },
  {
    path: 'en',
    children: mainRoutes,
  },
  {
    path: '**',
    redirectTo: '/pl/404',
  },
];
