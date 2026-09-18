from __future__ import annotations

"""Helpers for the lineup summary API."""

import json
from pathlib import Path
from typing import Any
from collections import defaultdict
from itertools import combinations
from app.dbmodels.models import Player, Possession

SAMPLE_SUMMARY_DATA_PATH = Path(__file__).resolve().parent / 'sample_summary_data' / 'sample_summary_data.json'
LineupRecord = dict[str, Any]
STAT_FIELDS = [
    'points', 'shot_attempts', 'fg2_made', 'fg2_attempted', 'fg3_made', 'fg3_attempted',
    'fg_made', 'fg_attempted', 'ft_made', 'ft_attempted', 'rebounds_offense', 'rebounds_defense',
    'rebound_opportunities', 'assists', 'steals', 'turnovers', 'blocks', 'offensive_fouls',
    'defensive_fouls', 'shooting_fouls', 'shot_attempt_points', 'ft_potential_points',
    'transition_take_fouls',
]

def safe_division(num, denom, multiplier=1.0):
    return ((num / denom) * multiplier) if denom else 0


def _normalize_lineup_size(lineup_size: Any) -> int:
    try:
        normalized_lineup_size = int(lineup_size)
    except (TypeError, ValueError):
        return 5

    return max(1, min(5, normalized_lineup_size))


def _load_sample_lineups() -> list[LineupRecord]:
    with open(SAMPLE_SUMMARY_DATA_PATH) as sample_summary_data_file:
        return json.load(sample_summary_data_file)


def _truncate_sample_lineup(lineup: LineupRecord, lineup_size: int) -> LineupRecord:
    truncated_lineup = dict(lineup)
    truncated_lineup['player_ids'] = lineup['player_ids'][:lineup_size]
    truncated_lineup['players'] = lineup['players'][:lineup_size]
    return truncated_lineup


def _get_sample_lineups(lineup_size: int = 5) -> list[LineupRecord]:
    normalized_lineup_size = _normalize_lineup_size(lineup_size)
    return [
        _truncate_sample_lineup(lineup, normalized_lineup_size)
        for lineup in _load_sample_lineups()
    ]

def normalize_lineup_size(lineup_size):
    try:
        val = int(lineup_size)
        return max(1, min(5, val))
    except (TypeError, ValueError):
        return 5
        

def get_lineup_league_summary_stats(lineup_size: int = 5) -> list[LineupRecord]:
    """Return lineup summaries across the entire league."""
    size = _normalize_lineup_size(lineup_size)

    # 1. Cache players {player_id_str: {player_id, name}}
    players = {
        str(p.id): {'player_id': str(p.id), 'name': p.name}
        for p in Player.objects.all()
    }

    # Lineup accumulator: (team_id, sorted_lineup_tuple) -> aggregated stats dict
    lineup_stats: dict[tuple[str, tuple[str, ...]], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # 2. Iterate through all possessions and aggregate stats
    for poss in Possession.objects.values('offensive_team_id', 'defensive_team_id', 'offensive_player_ids', 'defensive_player_ids', *STAT_FIELDS):
        off_team = str(poss['offensive_team_id'])
        def_team = str(poss['defensive_team_id'])
        off_players = sorted([str(pid) for pid in poss['offensive_player_ids']])
        def_players = sorted([str(pid) for pid in poss['defensive_player_ids']])

        # Generate n-man combinations (if size == 5, just the 5-man tuple)
        off_combos = [tuple(off_players)] if size == 5 else list(combinations(off_players, size))
        def_combos = [tuple(def_players)] if size == 5 else list(combinations(def_players, size))

        # Accumulate offensive stats for the offensive lineup
        for lineup in off_combos:
            acc = lineup_stats[(off_team, lineup)]
            acc['offensive_possessions'] += 1
            for field in STAT_FIELDS:
                acc[f'offensive_{field}'] += poss[field]

        # Accumulate defensive stats for the defensive lineup
        for lineup in def_combos:
            acc = lineup_stats[(def_team, lineup)]
            acc['defensive_possessions'] += 1
            for field in STAT_FIELDS:
                acc[f'defensive_{field}'] += poss[field]

    # 3. Format results and calculate advanced analytics
    results: list[LineupRecord] = []

    for (team_id, player_ids), stats in lineup_stats.items():
        off_poss = stats['offensive_possessions']
        def_poss = stats['defensive_possessions']
        total_poss = off_poss + def_poss

        # Analytics: Ratings per 100 possessions
        ortg = safe_division(stats['offensive_points'], off_poss, 100.0)
        drtg = safe_division(stats['defensive_points'], def_poss, 100.0)

        record: LineupRecord = {
            **stats,
            'total_possessions': total_poss,
            'team_id': team_id,
            'player_ids': list(player_ids),
            'players': [players.get(pid, {'player_id': pid, 'name': 'Unknown'}) for pid in player_ids],
            # Standard shooting %
            'offensive_fg_pct': safe_division(stats['offensive_fg_made'], stats['offensive_fg_attempted']),
            'offensive_fg2_pct': safe_division(stats['offensive_fg2_made'], stats['offensive_fg2_attempted']),
            'offensive_fg3_pct': safe_division(stats['offensive_fg3_made'], stats['offensive_fg3_attempted']),
            'defensive_fg_pct': safe_division(stats['defensive_fg_made'], stats['defensive_fg_attempted']),
            'defensive_fg2_pct': safe_division(stats['defensive_fg2_made'], stats['defensive_fg2_attempted']),
            'defensive_fg3_pct': safe_division(stats['defensive_fg3_made'], stats['defensive_fg3_attempted']),
            # Advanced Analytics
            'offensive_rating': round(ortg, 2),
            'defensive_rating': round(drtg, 2),
            'net_rating': round(ortg - drtg, 2),
            'offensive_reb_pct': safe_division(stats['offensive_rebounds_offense'], stats['offensive_rebound_opportunities']),
            'defensive_reb_pct': safe_division(stats['defensive_rebounds_defense'], stats['defensive_rebound_opportunities']),
        }
        results.append(record)

    # Sort results by net_rating descending
    results.sort(key=lambda r: r.get('net_rating', 0), reverse=True)
    return results
