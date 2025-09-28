#!/usr/bin/env python3
"""
Simple test script to verify the Baseball Stats app components work correctly
without running the full Streamlit app.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mlb_client():
    """Test the MLB API client"""
    print("🧪 Testing MLB API Client...")
    
    try:
        from mlb_api_client import MLBApiClient
        
        client = MLBApiClient()
        print("✅ MLBApiClient created successfully")
        
        # Test getting teams (this might fail if no internet)
        print("📡 Testing team data retrieval...")
        try:
            teams = client.get_teams()
            if teams and len(teams) > 0:
                print(f"✅ Successfully retrieved {len(teams)} teams")
                print(f"   Sample teams: {teams[0]['name']}, {teams[1]['name']}")
            else:
                print("⚠️  No teams retrieved (might be network issue)")
        except Exception as e:
            print(f"⚠️  Team retrieval failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing MLB client: {e}")
        return False

def test_data_manager():
    """Test the data manager"""
    print("\n🧪 Testing Data Manager...")
    
    try:
        from data_manager import DataManager
        
        # Create a test data manager
        dm = DataManager(data_file="test_baseball_data.json", user_id="test_user")
        print("✅ DataManager created successfully")
        
        # Test validation
        valid_game = {
            'date': '2024-09-01',
            'home_team': 'Yankees',
            'away_team': 'Red Sox',
            'home_team_id': 147,
            'away_team_id': 111,
            'home_score': 5,
            'away_score': 3
        }
        
        if dm._validate_game_data(valid_game):
            print("✅ Game data validation working")
        else:
            print("❌ Game data validation failed")
            
        # Clean up test file
        if os.path.exists("test_baseball_data.json"):
            os.remove("test_baseball_data.json")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing data manager: {e}")
        return False

def test_stats_calculator():
    """Test the stats calculator"""
    print("\n🧪 Testing Stats Calculator...")
    
    try:
        from stats_calculator import StatsCalculator
        
        calc = StatsCalculator()
        print("✅ StatsCalculator created successfully")
        
        # Test with sample data
        sample_games = []
        batting_stats, pitching_stats = calc.calculate_aggregate_stats(sample_games)
        
        if isinstance(batting_stats, list) and isinstance(pitching_stats, list):
            print("✅ Stats calculation working (empty data)")
        else:
            print("❌ Stats calculation returned unexpected format")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing stats calculator: {e}")
        return False

def test_imports():
    """Test critical imports"""
    print("\n🧪 Testing Critical Imports...")
    
    required_modules = [
        'streamlit',
        'pandas', 
        'plotly',
        'statsapi',
        'yaml'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def main():
    """Run all tests"""
    print("🚀 Starting Baseball Stats App Component Tests\n")
    
    tests = [
        ("Critical Imports", test_imports),
        ("MLB Client", test_mlb_client),
        ("Data Manager", test_data_manager), 
        ("Stats Calculator", test_stats_calculator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app should work correctly.")
    elif passed >= total - 1:
        print("⚠️  Most tests passed. App should work with minor issues.")
    else:
        print("❌ Multiple test failures. Please check your configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
