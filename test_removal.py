#!/usr/bin/env python3
"""
Test the new remove_game_by_properties method
"""
from data_manager import DataManager

# Test the removal by properties
dm = DataManager(user_id='test_remove')

# Clear any existing data
dm.clear_all_data()

# Add test games
test_games = [
    {'date': '2024-04-15', 'home_team': 'Yankees', 'away_team': 'Red Sox', 'home_team_id': 147, 'away_team_id': 111, 'home_score': 5, 'away_score': 3},
    {'date': '2024-04-27', 'home_team': 'Yankees', 'away_team': 'Angels', 'home_team_id': 147, 'away_team_id': 108, 'home_score': 8, 'away_score': 2, 'is_doubleheader': True, 'game_number': 1},
    {'date': '2024-04-27', 'home_team': 'Yankees', 'away_team': 'Angels', 'home_team_id': 147, 'away_team_id': 108, 'home_score': 4, 'away_score': 3, 'is_doubleheader': True, 'game_number': 2}
]

for game in test_games:
    dm.add_game(game, 'Test game')

print("Before removal:")
games = dm.get_all_games()
for i, game in enumerate(games):
    print(f"  {i}: {game.get('date')} - {game.get('away_team')} @ {game.get('home_team')} (Game #{game.get('game_number', 'N/A')})")

# Test removing the doubleheader game 1
print(f"\nRemoving Yankees vs Angels on 2024-04-27, Game 1...")
success = dm.remove_game_by_properties('2024-04-27', 147, 108, 1)
print(f"Removal success: {success}")

print("\nAfter removal:")
games = dm.get_all_games()
for i, game in enumerate(games):
    print(f"  {i}: {game.get('date')} - {game.get('away_team')} @ {game.get('home_team')} (Game #{game.get('game_number', 'N/A')})")
