from __future__ import annotations

"""Helpers for the lineup summary API."""

import json
from pathlib import Path
from typing import Any

SAMPLE_SUMMARY_DATA_PATH = Path(__file__).resolve().parent / 'sample_summary_data' / 'sample_summary_data.json'
LineupRecord = dict[str, Any]


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


def get_lineup_league_summary_stats(lineup_size: int = 5) -> list[LineupRecord]:
    """Return lineup summaries across the entire league."""
    # TODO: replace with your own implementation
    return _get_sample_lineups(lineup_size=lineup_size)
