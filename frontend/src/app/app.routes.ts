import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'lineups-summary' },
  {
    path: 'lineups-summary',
    loadComponent: () =>
      import('./lineups-summary/lineups-summary.component').then((m) => m.LineupsSummaryComponent),
  },
  {
    path: 'lineups-summary-api',
    loadComponent: () =>
      import('./lineups-summary-response/lineups-summary-response.component').then(
        (m) => m.LineupsSummaryResponseComponent,
      ),
  },
  { path: '**', redirectTo: 'lineups-summary' },
];
