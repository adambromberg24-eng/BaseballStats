#!/usr/bin/env python3
"""
Simple debug test for data saving
"""
import json
from data_manager import DataManager

def simple_save_test():
    print("=== Simple Save Test ===")
    
    # Test with basic game data
    data_manager = DataManager(user_id="simple_test")
    
    # Create minimal valid game data
    test_data = {
        'date': '2024-04-27',
        'home_team': 'New York Yankees',
        'away_team': 'Los Angeles Angels', 
        'home_team_id': 147,
        'away_team_id': 108,
        'home_score': 5,
        'away_score': 3,
        'venue': 'Yankee Stadium',
        'game_status': 'Final'
    }
    
    print("Testing basic save...")
    result = data_manager.add_game(test_data, "Test game")
    print(f"Basic save result: {result}")
    
    # Now test doubleheader data
    doubleheader_data = {
        'date': '2024-04-27',
        'home_team': 'New York Yankees',
        'away_team': 'Los Angeles Angels',
        'home_team_id': 147,
        'away_team_id': 108, 
        'home_score': 3,
        'away_score': 2,
        'venue': 'Yankee Stadium',
        'game_status': 'Final',
        'is_doubleheader': True,
        'game_number': 1
    }
    
    print("Testing doubleheader save...")
    result2 = data_manager.add_game(doubleheader_data, "Doubleheader game 1")
    print(f"Doubleheader save result: {result2}")

if __name__ == "__main__":
    simple_save_test()
