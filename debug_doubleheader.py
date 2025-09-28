#!/usr/bin/env python3
"""
Debug script for doubleheader save issues
"""
import json
import os
from data_manager import DataManager
from mlb_api_client import MLBApiClient

def test_doubleheader_save():
    print("=== Testing Doubleheader Save Logic ===")
    
    # Initialize managers
    data_manager = DataManager(user_id="debug_test")
    mlb_client = MLBApiClient()
    
    # Test Yankees doubleheader on April 27th, 2024
    print("\n1. Testing Yankees doubleheader data fetch...")
    
    # Yankees (147) vs some opponent
    yankees_id = 147
    
    # Try to get game options for Yankees on April 27, 2024
    try:
        game_options = mlb_client.get_game_options(yankees_id, None, "2024-04-27")
        print(f"Found {len(game_options)} game options")
        
        for i, option in enumerate(game_options):
            print(f"  Option {i}: {option['description']}")
    except Exception as e:
        print(f"Error getting game options: {e}")
        return
    
    # Test saving each game
    for i, option in enumerate(game_options):
        print(f"\n2. Testing save for game {i+1}...")
        
        try:
            # Get game data for this specific game
            game_data = mlb_client.get_game_data(yankees_id, None, "2024-04-27", game_selection=i)
            
            if game_data:
                print(f"Game data retrieved: {json.dumps(game_data, indent=2)}")
                
                # Try to save it
                success = data_manager.add_game(game_data, f"Debug test game {i+1}")
                
                print(f"Save result: {success}")
                
                if not success:
                    print("FAILED TO SAVE!")
                    break
            else:
                print("No game data retrieved")
        
        except Exception as e:
            print(f"Error in save test: {e}")
            import traceback
            traceback.print_exc()

def test_manual_doubleheader_data():
    print("\n=== Testing Manual Doubleheader Data ===")
    
    data_manager = DataManager(user_id="debug_manual")
    
    # Create test doubleheader game data
    test_game_data = {
        'date': '2024-04-27',
        'home_team': 'New York Yankees',
        'away_team': 'Los Angeles Angels',
        'home_team_id': 147,
        'away_team_id': 108,
        'home_score': 5,
        'away_score': 3,
        'venue': 'Yankee Stadium',
        'game_status': 'Final',
        'is_doubleheader': True,
        'game_number': 1,
        'inning': '9',
        'inning_state': 'End'
    }
    
    print(f"Test game data: {json.dumps(test_game_data, indent=2)}")
    
    try:
        success = data_manager.add_game(test_game_data, "Manual test game")
        print(f"Manual save result: {success}")
        
        if success:
            print("SUCCESS: Manual doubleheader data saved!")
            
            # Verify it's in the data
            games = data_manager.get_all_games()
            print(f"Total games in database: {len(games)}")
            
            for game in games:
                if game.get('is_doubleheader'):
                    print(f"Found doubleheader: {game}")
        else:
            print("FAILED: Manual doubleheader save failed")
            
    except Exception as e:
        print(f"Exception during manual save: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_doubleheader_data()
    print("\n" + "="*50)
    test_doubleheader_save()
