import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.helpers.lineups import get_lineup_league_summary_stats

lineups = get_lineup_league_summary_stats(lineup_size=5)

print("TOP REBOUNDING COUNTER LINEUPS:\n")

# Use .get() to safely default to 0 if a stat was never triggered
qualified = [
    l for l in lineups 
    if (l.get('offensive_rebound_opportunities', 0) + l.get('defensive_rebound_opportunities', 0)) >= 3
]

qualified.sort(
    key=lambda x: (x.get('defensive_reb_pct', 0), x.get('offensive_reb_pct', 0), x.get('net_rating', 0)), 
    reverse=True
)

for l in qualified[:5]:
    names = [p['name'] for p in l['players']]
    d_reb_made = l.get('defensive_rebounds_defense', 0)
    d_reb_opp = l.get('defensive_rebound_opportunities', 0)
    d_pct = l.get('defensive_reb_pct', 0) * 100

    o_reb_made = l.get('offensive_rebounds_offense', 0)
    o_reb_opp = l.get('offensive_rebound_opportunities', 0)
    o_pct = l.get('offensive_reb_pct', 0) * 100

    print(f"Team: {l['team_id']}")
    print(f"Lineup: {', '.join(names)}")
    print(f"Defensive Rebounds: {d_reb_made}/{d_reb_opp} ({d_pct:.1f}%)")
    print(f"Offensive Rebounds: {o_reb_made}/{o_reb_opp} ({o_pct:.1f}%)")
    print(f"Net Rating: {l.get('net_rating', 0):+0.2f} | Total Possessions: {l.get('total_possessions', 0)}\n")