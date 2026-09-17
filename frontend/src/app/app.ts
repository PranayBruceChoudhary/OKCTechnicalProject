import { Component, OnInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterOutlet } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { filter } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

enum Tab {
  FRONTEND,
  BACKEND,
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, MatTabsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly router = inject(Router);

  readonly tab = Tab;
  currentTab: Tab = Tab.FRONTEND;

  constructor() {
    this.router.events
      .pipe(
        filter((event): event is NavigationEnd => event instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.setActiveTab());
  }

  ngOnInit(): void {
    this.setActiveTab();
  }

  setActiveTab(): void {
    if (this.router.url.includes('lineups-summary-api')) {
      this.currentTab = Tab.BACKEND;
      return;
    }
    this.currentTab = Tab.FRONTEND;
  }
}
