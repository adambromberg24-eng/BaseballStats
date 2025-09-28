#!/usr/bin/env python3
"""
Test the doubleheader functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_doubleheader():
    """Test Yankees doubleheader on April 27th"""
    from mlb_api_client import MLBApiClient
    
    client = MLBApiClient()
    
    # Yankees team ID is 147
    # Let's test with a known opponent
    print("Testing doubleheader functionality...")
    
    # Test getting game options first
    options = client.get_game_options(147, 111, "2024-04-27")  # Yankees vs Red Sox example
    
    if options:
        print(f"✅ Found {len(options)} game options:")
        for i, option in enumerate(options):
            print(f"  {i}: {option['description']}")
            
        # Test getting specific game data
        if len(options) > 0:
            game_data = client.get_game_data(147, 111, "2024-04-27", game_selection=0)
            if game_data:
                print(f"✅ Game data retrieved:")
                print(f"   Score: {game_data.get('away_team')} {game_data.get('away_score')} - {game_data.get('home_team')} {game_data.get('home_score')}")
                print(f"   Date: {game_data.get('date')}")
                print(f"   Status: {game_data.get('game_status')}")
                print(f"   Doubleheader: {game_data.get('is_doubleheader')}")
                return True
    else:
        print("⚠️  No games found for test date")
        
    return False

if __name__ == "__main__":
    try:
        success = test_doubleheader()
        if success:
            print("\n🎉 Doubleheader functionality test passed!")
        else:
            print("\n⚠️  Test completed but no doubleheader found")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
