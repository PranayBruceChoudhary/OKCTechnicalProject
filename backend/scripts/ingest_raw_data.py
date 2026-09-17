# Potential Solution for ingesting raw data

import json
import os
from pathlib import Path

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

django.setup()

from django.db import transaction
from app.dbmodels.models import Game, Team, Player, Possession

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / 'raw_data'

POSSESSION_COUNTING_FIELDS = (
    'period',
    'seconds',
    'fg2_made',
    'fg2_attempted',
    'fg3_made',
    'fg3_attempted',
    'fg_made',
    'fg_attempted',
    'ft_made',
    'ft_attempted',
    'rebounds_offense',
    'rebounds_defense',
    'rebound_opportunities',
    'assists',
    'steals',
    'turnovers',
    'blocks',
    'offensive_fouls',
    'defensive_fouls',
    'shooting_fouls',
    'points',
    'shot_attempts',
    'shot_attempt_points',
    'ft_potential_points',
    'transition_take_fouls',
)


def load_json(filename):
    with open(RAW_DATA_DIR / filename) as raw_file:
        return json.load(raw_file)


def delete_possessions():
    Possession.objects.all().delete()


def delete_players():
    Player.objects.all().delete()


def delete_teams():
    Team.objects.all().delete()


def delete_games():
    Game.objects.all().delete()


def ingest_teams():
    teams = [Team(id=team['team_id'], name=team['name']) for team in load_json('teams.json')]
    Team.objects.bulk_create(teams)


def ingest_games():
    games = [Game(id=game['game_id'], date=game['date']) for game in load_json('games.json')]
    Game.objects.bulk_create(games)


def ingest_players():
    players = [
        Player(id=player['player_id'], name=player['name'], team_id=player['team_id'])
        for player in load_json('players.json')
    ]
    Player.objects.bulk_create(players)


def ingest_possessions():
    possessions = [
        Possession(
            id=row['possession_id'],
            game_id=row['game_id'],
            offensive_team_id=row['offensive_team_id'],
            defensive_team_id=row['defensive_team_id'],
            offensive_player_ids=row['offensive_player_ids'],
            defensive_player_ids=row['defensive_player_ids'],
            **{field: row[field] for field in POSSESSION_COUNTING_FIELDS},
        )
        for row in load_json('possessions.json')
    ]
    Possession.objects.bulk_create(possessions)

if __name__ == '__main__':
    with transaction.atomic():
        delete_possessions()
        delete_players()
        delete_teams()
        delete_games()

        ingest_teams()
        ingest_games()
        ingest_players()
        ingest_possessions()
