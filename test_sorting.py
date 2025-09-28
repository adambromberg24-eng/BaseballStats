#!/usr/bin/env python3
"""
Test reverse chronological sorting
"""
from data_manager import DataManager

# Test the sorting logic
dm = DataManager(user_id='test_sort')

# Clear any existing data
dm.clear_all_data()

# Add some test games with different dates
test_games = [
    {'date': '2024-04-15', 'home_team': 'Yankees', 'away_team': 'Red Sox', 'home_team_id': 147, 'away_team_id': 111, 'home_score': 5, 'away_score': 3},
    {'date': '2024-04-27', 'home_team': 'Yankees', 'away_team': 'Angels', 'home_team_id': 147, 'away_team_id': 108, 'home_score': 8, 'away_score': 2},
    {'date': '2024-04-10', 'home_team': 'Dodgers', 'away_team': 'Giants', 'home_team_id': 119, 'away_team_id': 137, 'home_score': 6, 'away_score': 4}
]

for game in test_games:
    result = dm.add_game(game, 'Test game')
    print(f"Added game {game['date']}: {result}")

# Get games and sort in reverse chronological order
games = dm.get_all_games()
print(f"\nOriginal order ({len(games)} games):")
for game in games:
    print(f"  {game.get('date')}: {game.get('away_team')} @ {game.get('home_team')}")

games.sort(key=lambda x: x.get('date', ''), reverse=True)
print(f"\nReverse chronological order:")
for game in games:
    print(f"  {game.get('date')}: {game.get('away_team')} @ {game.get('home_team')}")
