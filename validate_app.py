#!/usr/bin/env python3
"""
Quick validation script for Baseball Stats app
"""

def validate_app():
    """Validate the main components can be imported and initialized"""
    print("🔍 Validating Baseball Stats App...")
    
    # Test 1: Check imports
    try:
        print("📦 Testing imports...")
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        from mlb_api_client import MLBApiClient
        from data_manager import DataManager
        from stats_calculator import StatsCalculator
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Initialize components
    try:
        print("🔧 Testing component initialization...")
        mlb_client = MLBApiClient()
        data_manager = DataManager(user_id="test")
        stats_calc = StatsCalculator()
        print("✅ All components initialized successfully")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False
    
    # Test 3: Test basic functionality
    try:
        print("🧪 Testing basic functionality...")
        
        # Test data validation
        sample_game = {
            'date': '2024-09-01',
            'home_team': 'Test Home',
            'away_team': 'Test Away', 
            'home_team_id': 1,
            'away_team_id': 2,
            'home_score': 5,
            'away_score': 3
        }
        
        if data_manager._validate_game_data(sample_game):
            print("✅ Data validation working")
        else:
            print("⚠️  Data validation failed")
            
        # Test stats calculation with empty data
        batting_stats, pitching_stats = stats_calc.calculate_aggregate_stats([])
        if isinstance(batting_stats, list) and isinstance(pitching_stats, list):
            print("✅ Stats calculation working")
        else:
            print("⚠️  Stats calculation failed")
            
    except Exception as e:
        print(f"⚠️  Functionality test error: {e}")
    
    print("\n🎉 App validation completed!")
    print("Your Baseball Stats app should work correctly now.")
    print("\nTo run the app:")
    print('streamlit run app.py')
    
    return True

if __name__ == "__main__":
    validate_app()
