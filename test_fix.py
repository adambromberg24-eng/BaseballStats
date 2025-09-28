#!/usr/bin/env python3
"""
Test the fixed remove_game_by_properties method with various data types
"""
from data_manager import DataManager

# Test with mixed data types
dm = DataManager(user_id='test_fix')
dm.clear_all_data()

# Add a test game with string team IDs (like from JSON)
test_game = {
    'date': '2024-04-15', 
    'home_team': 'Yankees', 
    'away_team': 'Red Sox', 
    'home_team_id': '147',  # String instead of int
    'away_team_id': '111',  # String instead of int
    'home_score': 5, 
    'away_score': 3
}

print("Testing with string team IDs...")
result = dm.add_game(test_game, 'Test game')
print(f"Add game result: {result}")

# Test removal with integer team IDs
print("\nTesting removal with integer team IDs...")
success = dm.remove_game_by_properties('2024-04-15', 147, 111, None)
print(f"Removal success: {success}")

# Test removal with string team IDs
dm.add_game(test_game, 'Test game 2')
print("\nTesting removal with string team IDs...")
success = dm.remove_game_by_properties('2024-04-15', '147', '111', None)
print(f"Removal success: {success}")

# Test with doubleheader game
doubleheader_game = {
    'date': '2024-04-27', 
    'home_team': 'Yankees', 
    'away_team': 'Angels', 
    'home_team_id': '147',
    'away_team_id': '108',
    'home_score': 5, 
    'away_score': 3,
    'is_doubleheader': True,
    'game_number': '1'  # String game number
}

print("\nTesting doubleheader with string game_number...")
result = dm.add_game(doubleheader_game, 'Doubleheader game')
print(f"Add doubleheader result: {result}")

print("\nTesting doubleheader removal...")
success = dm.remove_game_by_properties('2024-04-27', 147, 108, 1)
print(f"Doubleheader removal success: {success}")

print("\nRemaining games:")
games = dm.get_all_games()
for game in games:
    print(f"  {game.get('date')}: {game.get('away_team')} @ {game.get('home_team')}")
    
print(f"\nTotal games remaining: {len(games)}")
