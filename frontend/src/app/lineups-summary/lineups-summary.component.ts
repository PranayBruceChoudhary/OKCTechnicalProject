import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

export interface Player {
  player_id: string;
  name: string;
}

export interface LineupSummary {
  team_id: string;
  total_possessions: number;
  offensive_possessions: number;
  defensive_possessions: number;
  offensive_points: number;
  defensive_points: number;
  net_rating: number;
  offensive_rating: number;
  defensive_rating: number;
  offensive_reb_pct: number;
  defensive_reb_pct: number;
  offensive_fg_pct: number;
  defensive_fg_pct: number;
  offensive_assists: number;
  offensive_turnovers: number;
  defensive_steals: number;
  defensive_blocks: number;
  player_ids: string[];
  players: Player[];
  trueSkillScore?: number;
  strengthsSummary?: string[];
}

export interface CriteriaMask {
  rebounds: boolean;
  shooting: boolean;
  assists: boolean;
  defense: boolean;
  netRating: boolean;
}

@Component({
  selector: 'app-lineups-summary',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './lineups-summary.component.html',
  styleUrls: ['./lineups-summary.component.scss']
})
export class LineupsSummaryComponent implements OnInit {
  selectedLineupSize: number = 5;

  criteriaMask: CriteriaMask = {
    rebounds: true,
    shooting: true,
    assists: false,
    defense: true,
    netRating: true
  };

  rawLineups: LineupSummary[] = [];
  topRankedLineups: LineupSummary[] = [];
  isLoading: boolean = false;
  hasEvaluated: boolean = false;

  private backendUrl = 'http://127.0.0.1:8000/api/v1/lineups';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchDataAndEvaluate();
  }

  fetchDataAndEvaluate(): void {
    this.isLoading = true;
    const url = `${this.backendUrl}?lineup_size=${this.selectedLineupSize}`;

    this.http.get<LineupSummary[]>(url).subscribe({
      next: (data) => {
        this.rawLineups = data || [];
        this.executeEvaluation();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load lineups from API:', err);
        this.isLoading = false;
      }
    });
  }

  onGetResult(): void {
    this.fetchDataAndEvaluate();
  }

  private executeEvaluation(): void {
    if (!this.rawLineups || this.rawLineups.length === 0) {
      this.topRankedLineups = [];
      this.hasEvaluated = true;
      return;
    }

    const scoredLineups = this.rawLineups.map((lineup) => {
      const { score, strengths } = this.computeTrueSkill(lineup, this.criteriaMask);
      return {
        ...lineup,
        trueSkillScore: score,
        strengthsSummary: strengths
      };
    });

    scoredLineups.sort((a, b) => (b.trueSkillScore ?? 0) - (a.trueSkillScore ?? 0));
    this.topRankedLineups = scoredLineups.slice(0, 3);
    this.hasEvaluated = true;
  }

  public computeTrueSkill(lineup: LineupSummary, mask: CriteriaMask): { score: number; strengths: string[] } {
    let totalWeight = 0;
    let accumulatedScore = 0;
    const strengths: string[] = [];

    // Rebound Criteria
    if (mask.rebounds) {
      const weight = 20;
      totalWeight += weight;
      const dRebPct = lineup.defensive_reb_pct || 0;
      const oRebPct = lineup.offensive_reb_pct || 0;
      const reboundIndex = (dRebPct * 0.7 + oRebPct * 0.3) * 100;
      accumulatedScore += Math.min(100, Math.max(0, reboundIndex)) * weight;

      if (dRebPct >= 0.75) {
        strengths.push(`Glass Control: ${(dRebPct * 100).toFixed(0)}% D-REB`);
      }
    }

    // Shooting Criteria
    if (mask.shooting) {
      const weight = 25;
      totalWeight += weight;
      const fgPct = lineup.offensive_fg_pct || 0;
      const shootingScore = Math.min(100, fgPct * 140);
      accumulatedScore += shootingScore * weight;

      if (fgPct >= 0.5) {
        strengths.push(`High Efficiency: ${(fgPct * 100).toFixed(1)}% FG`);
      }
    }

    // Assist Criteria
    if (mask.assists) {
      const weight = 15;
      totalWeight += weight;
      const astRate = lineup.offensive_possessions > 0 
        ? (lineup.offensive_assists / lineup.offensive_possessions) 
        : 0;
      const assistScore = Math.min(100, astRate * 250);
      accumulatedScore += assistScore * weight;

      if (lineup.offensive_assists >= 2) {
        strengths.push(`Ball Movement: ${lineup.offensive_assists} Total Assists`);
      }
    }

    // Defense Criteria
    if (mask.defense) {
      const weight = 20;
      totalWeight += weight;
      const drtg = lineup.defensive_rating || 120;
      const defenseScore = Math.min(100, Math.max(0, (140 - drtg) * (100 / 60)));
      accumulatedScore += defenseScore * weight;

      if (drtg <= 100) {
        strengths.push(`Defense: Held opponents to ${drtg.toFixed(1)} DRTG`);
      }
    }

    // Net Rating Criteria
    if (mask.netRating) {
      const weight = 20;
      totalWeight += weight;
      const net = lineup.net_rating || 0;
      const netScore = Math.min(100, Math.max(0, net + 50));
      accumulatedScore += netScore * weight;

      if (net > 0) {
        strengths.push(`Net Impact: ${net > 0 ? '+' : ''}${net.toFixed(1)} Net Rating`);
      }
    }

    if (totalWeight === 0) {
      return { score: lineup.total_possessions, strengths: ['Ranked by Total Possessions'] };
    }

    const finalScore = Math.round(accumulatedScore / totalWeight);
    if (strengths.length === 0) {
      strengths.push('Solid all-around baseline metrics');
    }

    return { score: finalScore, strengths };
  }
}