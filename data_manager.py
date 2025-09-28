import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class DataManager:
    def __init__(self, data_file: str = "baseball_data.json", user_id: str = None):
        self.user_id = user_id
        self.data_file = f"baseball_data_{user_id}.json" if user_id else data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file or create empty structure"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"games": [], "created_at": datetime.now().isoformat()}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {"games": [], "created_at": datetime.now().isoformat()}
    
    def _save_data(self) -> bool:
        """Save data to JSON file"""
        try:
            print(f"DEBUG: Attempting to save to file: {self.data_file}")
            self.data["updated_at"] = datetime.now().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
            print(f"DEBUG: Successfully saved {len(self.data.get('games', []))} games")
            return True
        except Exception as e:
            print(f"DEBUG: Error saving data: {e}")
            return False
    
    def add_game(self, game_data: Dict[str, Any], notes: str = "") -> bool:
        """Add a new game to the database with validation"""
        try:
            # Debug: Print game data being validated
            print(f"DEBUG: Attempting to add game data: {game_data}")
            
            # Validate game data
            validation_result, validation_error = self._validate_game_data_with_debug(game_data)
            if not validation_result:
                print(f"DEBUG: Validation failed: {validation_error}")
                return False
                
            # Check if game already exists - modified for doubleheader support
            base_game_id = f"{game_data.get('date')}_{game_data.get('home_team_id')}_{game_data.get('away_team_id')}"
            
            # For the new game, create the full ID
            game_id = base_game_id
            
            is_doubleheader = game_data.get('is_doubleheader')
            game_number = game_data.get('game_number')
            
            # Handle different boolean representations (True, "true", 1, etc.)
            if is_doubleheader in [True, "true", "True", 1, "1"]:
                is_doubleheader = True
            else:
                is_doubleheader = False
            
            # Handle different number representations
            if game_number is not None:
                try:
                    game_number = int(game_number)
                except (ValueError, TypeError):
                    game_number = None
            
            if is_doubleheader and game_number:
                game_id += f"_game{game_number}"
            
            print(f"DEBUG: Generated game_id: {game_id}")
            
            for existing_game in self.data["games"]:
                existing_base_id = f"{existing_game.get('date')}_{existing_game.get('home_team_id')}_{existing_game.get('away_team_id')}"
                
                # For existing games, create the full ID
                existing_id = existing_base_id
                if existing_game.get('is_doubleheader') and existing_game.get('game_number'):
                    existing_id += f"_game{existing_game.get('game_number')}"
                elif existing_game.get('game_number'):
                    # Handle case where game_number exists but is_doubleheader is False/missing
                    existing_id += f"_game{existing_game.get('game_number')}"
                
                # Exact match - this is a duplicate
                if existing_id == game_id:
                    print(f"DEBUG: Duplicate game detected. Existing ID: {existing_id}, New ID: {game_id}")
                    return False
                
                # Special case: if we're adding a doubleheader game and there's an existing game 
                # with the same base ID but no game number, we need to handle this differently
                if (game_data.get('is_doubleheader') and game_data.get('game_number') and 
                    existing_base_id == base_game_id and 
                    not existing_game.get('game_number')):
                    # This is allowed - different games in the doubleheader
                    continue
            
            # Sanitize notes
            notes = self._sanitize_notes(notes)
            
            # Add metadata to game data
            game_data["notes"] = notes
            game_data["added_at"] = datetime.now().isoformat()
            game_data["version"] = "1.0"
            
            print(f"DEBUG: Adding game to data structure. Final game data: {game_data}")
            self.data["games"].append(game_data)
            
            save_result = self._save_data()
            print(f"DEBUG: Save result: {save_result}")
            return save_result
        except Exception as e:
            print(f"Error adding game: {e}")
            return False
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all games from the database"""
        return self.data.get("games", [])
    
    def remove_game(self, index: int) -> bool:
        """Remove a game by index"""
        try:
            if 0 <= index < len(self.data["games"]):
                self.data["games"].pop(index)
                return self._save_data()
            return False
        except Exception as e:
            print(f"Error removing game: {e}")
            return False

    def remove_game_by_properties(self, date: str, home_team_id: int, away_team_id: int, game_number: int = None) -> bool:
        """Remove a game by its unique properties - Updated for deployment sync"""
        try:
            # Convert team IDs to integers to handle string inputs
            try:
                home_team_id = int(home_team_id) if home_team_id is not None else None
                away_team_id = int(away_team_id) if away_team_id is not None else None
            except (ValueError, TypeError):
                print(f"DEBUG: Invalid team IDs - home: {home_team_id}, away: {away_team_id}")
                return False
                
            # Convert game_number to int if provided
            if game_number is not None:
                try:
                    game_number = int(game_number)
                except (ValueError, TypeError):
                    game_number = None
                    
            print(f"DEBUG: Removing game with properties - date: {date}, home_team_id: {home_team_id}, away_team_id: {away_team_id}, game_number: {game_number}")
                    
            for i, game in enumerate(self.data["games"]):
                # Convert stored team IDs to int for comparison
                stored_home_id = int(game.get('home_team_id')) if game.get('home_team_id') is not None else None
                stored_away_id = int(game.get('away_team_id')) if game.get('away_team_id') is not None else None
                stored_game_number = int(game.get('game_number')) if game.get('game_number') is not None else None
                
                if (game.get('date') == date and 
                    stored_home_id == home_team_id and 
                    stored_away_id == away_team_id and
                    stored_game_number == game_number):
                    print(f"DEBUG: Found matching game at index {i}, removing...")
                    self.data["games"].pop(i)
                    save_result = self._save_data()
                    print(f"DEBUG: Game removal save result: {save_result}")
                    return save_result
            
            print(f"DEBUG: No matching game found for removal")
            return False
        except Exception as e:
            print(f"Error removing game by properties: {e}")
            return False
    
    def get_game_by_date_and_teams(self, date: str, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """Get a specific game by date and teams"""
        for game in self.data["games"]:
            if (game.get("date") == date and 
                game.get("home_team") == home_team and 
                game.get("away_team") == away_team):
                return game
        return None
    
    def get_games_by_team(self, team_name: str) -> List[Dict[str, Any]]:
        """Get all games involving a specific team"""
        games = []
        for game in self.data["games"]:
            if team_name in [game.get("home_team"), game.get("away_team")]:
                games.append(game)
        return games
    
    def get_games_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get games within a date range"""
        games = []
        for game in self.data["games"]:
            game_date = game.get("date", "")
            if start_date <= game_date <= end_date:
                games.append(game)
        return games
    
    def clear_all_data(self) -> bool:
        """Clear all game data"""
        try:
            self.data = {"games": [], "created_at": datetime.now().isoformat()}
            return self._save_data()
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def _validate_game_data_with_debug(self, game_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate game data structure and required fields with debug info"""
        required_fields = ['date', 'home_team', 'away_team', 'home_team_id', 'away_team_id']
        
        # Check required fields
        for field in required_fields:
            if field not in game_data:
                return False, f"Missing required field: {field}"
            if not game_data[field] and game_data[field] != 0:  # Allow 0 values
                return False, f"Empty required field: {field} (value: {game_data[field]})"
        
        # Validate date format
        try:
            datetime.strptime(game_data['date'], '%Y-%m-%d')
        except ValueError as e:
            return False, f"Invalid date format: {game_data['date']} - {e}"
        
        # Validate team IDs are integers
        try:
            int(game_data['home_team_id'])
        except (ValueError, TypeError) as e:
            return False, f"Invalid home_team_id: {game_data['home_team_id']} - {e}"
            
        try:
            int(game_data['away_team_id'])
        except (ValueError, TypeError) as e:
            return False, f"Invalid away_team_id: {game_data['away_team_id']} - {e}"
        
        # Validate scores if present
        if 'home_score' in game_data and game_data['home_score'] is not None:
            try:
                int(game_data['home_score'])
            except (ValueError, TypeError) as e:
                return False, f"Invalid home_score: {game_data['home_score']} - {e}"
                
        if 'away_score' in game_data and game_data['away_score'] is not None:
            try:
                int(game_data['away_score'])
            except (ValueError, TypeError) as e:
                return False, f"Invalid away_score: {game_data['away_score']} - {e}"
        
        return True, "Validation successful"

    def _validate_game_data(self, game_data: Dict[str, Any]) -> bool:
        """Validate game data structure and required fields"""
        required_fields = ['date', 'home_team', 'away_team', 'home_team_id', 'away_team_id']
        
        # Check required fields
        for field in required_fields:
            if field not in game_data or not game_data[field]:
                return False
        
        # Validate date format
        try:
            datetime.strptime(game_data['date'], '%Y-%m-%d')
        except ValueError:
            return False
        
        # Validate team IDs are integers
        try:
            int(game_data['home_team_id'])
            int(game_data['away_team_id'])
        except (ValueError, TypeError):
            return False
        
        # Validate scores if present
        if 'home_score' in game_data and game_data['home_score'] is not None:
            try:
                int(game_data['home_score'])
            except (ValueError, TypeError):
                return False
                
        if 'away_score' in game_data and game_data['away_score'] is not None:
            try:
                int(game_data['away_score'])
            except (ValueError, TypeError):
                return False
        
        return True
    
    def _sanitize_notes(self, notes: str) -> str:
        """Sanitize notes input by limiting length and removing problematic characters"""
        if not notes:
            return ""
        
        # Limit length
        notes = str(notes)[:1000]
        
        # Remove or replace problematic characters if needed
        notes = notes.strip()
        
        return notes