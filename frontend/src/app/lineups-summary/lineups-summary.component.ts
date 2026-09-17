import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { LineupsService } from '../_services/lineups.service';

@Component({
  selector: 'lineups-summary-component',
  templateUrl: './lineups-summary.component.html',
  styleUrl: './lineups-summary.component.scss',
})
export class LineupsSummaryComponent implements OnInit {
  private readonly lineupsService = inject(LineupsService);
  private readonly cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.lineupsService.getLineupsLeagueSummary().subscribe({
      next: (data) => {
        console.log(data.apiResponse);
        this.cdr.markForCheck();
      },
    });
  }
}
