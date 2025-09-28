import statsapi
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import time
import streamlit as st

class MLBApiClient:
    def __init__(self):
        self.teams_cache = None
        self.last_api_call = 0
        self.rate_limit_delay = 1  # Minimum seconds between API calls
    
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_call)
        self.last_api_call = time.time()
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get list of all MLB teams"""
        # Use simple caching instead of st.cache_data
        if self.teams_cache is not None:
            return self.teams_cache
            
        try:
            self._rate_limit()
            # Get teams using statsapi
            teams_data = statsapi.get('teams', {'sportId': 1})
            teams = []
            
            if teams_data and 'teams' in teams_data:
                for team in teams_data['teams']:
                    teams.append({
                        'id': team.get('id'),
                        'name': team.get('name', ''),
                        'abbreviation': team.get('abbreviation', ''),
                        'teamName': team.get('teamName', ''),
                        'locationName': team.get('locationName', ''),
                        'division': team.get('division', {}).get('name', ''),
                        'league': team.get('league', {}).get('name', '')
                    })
            
            # Sort teams by name
            teams.sort(key=lambda x: x['name'])
            self.teams_cache = teams  # Cache the result
            return teams
            
        except Exception as e:
            if 'st' in globals():
                st.error(f"Unable to load MLB teams: {str(e)}")
            print(f"Error fetching teams: {e}")
            return []
    
    def get_game_data(self, home_team_id: int, away_team_id: int, game_date: str, game_selection: int = None) -> Optional[Dict[str, Any]]:
        """Get game data for specific teams and date
        
        Args:
            home_team_id: ID of home team
            away_team_id: ID of away team  
            game_date: Date to search for games
            game_selection: Which game to select if multiple games (0 for first, 1 for second, etc.)
        """
        try:
            self._rate_limit()
            
            # Convert date to string format if it's a date object
            if hasattr(game_date, 'strftime'):
                date_str = game_date.strftime('%Y-%m-%d')
            else:
                date_str = str(game_date)
            
            # Check if we're in a Streamlit context before using UI elements
            show_ui = 'st' in globals() and hasattr(st, 'spinner')
            
            if show_ui:
                with st.spinner(f"Searching for games on {date_str}..."):
                    # Get schedule for the date
                    schedule = statsapi.schedule(date=date_str)
            else:
                print(f"Searching for games on {date_str}...")
                schedule = statsapi.schedule(date=date_str)
                
            # Find all matching games (handles doubleheaders and postponed games)
            matching_games = [
                game for game in schedule
                if game.get('home_id') == home_team_id and game.get('away_id') == away_team_id
            ]
            
            if not matching_games:
                if show_ui:
                    st.warning(f"No games found between these teams on {date_str}")
                else:
                    print(f"No games found between these teams on {date_str}")
                return None
            
            # Handle multiple games (doubleheader)
            if len(matching_games) > 1:
                if show_ui:
                    st.info(f"Found {len(matching_games)} games for this matchup (doubleheader)")
                else:
                    print(f"Found {len(matching_games)} games for this matchup (doubleheader)")
                
                # If no specific game selection, return game options for UI selection
                if game_selection is None:
                    return {"multiple_games": matching_games, "needs_selection": True}
            
            # Select the appropriate game
            if game_selection is not None and 0 <= game_selection < len(matching_games):
                target_game = matching_games[game_selection]
            else:
                # Default selection logic: prefer completed games with scores
                target_game = None
                for game in matching_games:
                    if game.get('status') in ['Final', 'Completed'] and (game.get('home_score', 0) > 0 or game.get('away_score', 0) > 0):
                        target_game = game
                        break
                
                # If no completed game found, take the first matching game
                if not target_game:
                    target_game = matching_games[0]
            
            if not target_game:
                if show_ui:
                    st.error("No suitable game found for the selected criteria")
                else:
                    print("No suitable game found for the selected criteria")
                return None
            
            game_id = target_game.get('game_id')
            if not game_id:
                if show_ui:
                    st.error("Invalid game ID retrieved")
                else:
                    print("Invalid game ID retrieved")
                return None
        
            if show_ui:
                with st.spinner("Fetching detailed game statistics..."):
                    # Get detailed box score
                    box_score = statsapi.boxscore_data(game_id)
            else:
                print("Fetching detailed game statistics...")
                box_score = statsapi.boxscore_data(game_id)
            
            # Extract game information with better score handling
            # Get actual game date and time from the target game
            game_datetime = target_game.get('game_datetime')
            actual_date = None
            if game_datetime:
                try:
                    dt = datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%SZ")
                    actual_date = dt.strftime("%Y-%m-%d")
                except:
                    # Try alternative format
                    try:
                        dt = datetime.strptime(game_datetime, "%Y-%m-%d")
                        actual_date = dt.strftime("%Y-%m-%d")
                    except:
                        pass

            # Get final scores with multiple fallback methods
            home_score = 0
            away_score = 0
            
            # Method 1: From target_game (schedule data)
            if target_game.get('home_score') is not None:
                home_score = int(target_game.get('home_score', 0))
            if target_game.get('away_score') is not None:
                away_score = int(target_game.get('away_score', 0))
                
            # Method 2: From box score data if schedule scores are 0
            if (home_score == 0 and away_score == 0) and box_score:
                # Try to extract from linescore
                if 'linescore' in box_score:
                    linescore = box_score['linescore']
                    if 'teams' in linescore:
                        if 'home' in linescore['teams'] and 'runs' in linescore['teams']['home']:
                            home_score = int(linescore['teams']['home']['runs'])
                        if 'away' in linescore['teams'] and 'runs' in linescore['teams']['away']:
                            away_score = int(linescore['teams']['away']['runs'])

            # Check if this is part of a doubleheader
            is_doubleheader = len(matching_games) > 1
            game_number = None
            if is_doubleheader:
                # Try to determine which game this is
                game_number = target_game.get('game_num', 1)
                if not game_number:
                    # Fallback: find position in matching games list
                    for idx, game in enumerate(matching_games):
                        if game.get('game_id') == game_id:
                            game_number = idx + 1
                            break
            
            # Get game status and venue info
            game_status = target_game.get('status', 'Unknown')
            venue = target_game.get('venue_name', 'Unknown Venue')
            
            game_data = {
                'game_id': game_id,
                'date': actual_date or date_str,  # Use actual game date as primary
                'input_date': date_str,  # Keep original input date for reference
                'actual_date': actual_date or date_str,
                'home_team': target_game.get('home_name', ''),
                'away_team': target_game.get('away_name', ''),
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'home_score': home_score,
                'away_score': away_score,
                'game_status': game_status,
                'venue': venue,
                'is_doubleheader': is_doubleheader,
                'game_number': game_number,
                'total_games_found': len(matching_games),
                'home_team_batting': [],
                'away_team_batting': [],
                'home_team_pitching': [],
                'away_team_pitching': []
            }
            
            # Extract batting statistics from homeBatters and awayBatters
            if 'homeBatters' in box_score:
                for player_stats in box_score['homeBatters']:
                    if player_stats.get('personId', 0) > 0:  # Skip header row (personId = 0)
                        batting_data = self._extract_batting_stats(player_stats, box_score)
                        if batting_data:
                            game_data['home_team_batting'].append(batting_data)
            
            if 'awayBatters' in box_score:
                for player_stats in box_score['awayBatters']:
                    if player_stats.get('personId', 0) > 0:  # Skip header row (personId = 0)
                        batting_data = self._extract_batting_stats(player_stats, box_score)
                        if batting_data:
                            game_data['away_team_batting'].append(batting_data)
            
            # Extract pitching statistics from homePitchers and awayPitchers
            if 'homePitchers' in box_score:
                for player_stats in box_score['homePitchers']:
                    if player_stats.get('personId', 0) > 0:  # Skip header row (personId = 0)
                        pitching_data = self._extract_pitching_stats(player_stats, box_score)
                        if pitching_data:
                            game_data['home_team_pitching'].append(pitching_data)
            
            if 'awayPitchers' in box_score:
                for player_stats in box_score['awayPitchers']:
                    if player_stats.get('personId', 0) > 0:  # Skip header row (personId = 0)
                        pitching_data = self._extract_pitching_stats(player_stats, box_score)
                        if pitching_data:
                            game_data['away_team_pitching'].append(pitching_data)
            
            return game_data
            
        except Exception as e:
            show_ui = 'st' in globals() and hasattr(st, 'error')
            if show_ui:
                st.error(f"Error fetching game data: {str(e)}")
                st.info("Please check your internet connection and try again.")
            else:
                print(f"Error fetching game data: {str(e)}")
                print("Please check your internet connection and try again.")
            print(f"Detailed error fetching game data: {e}")
            return None
    
    def _extract_batting_stats(self, player_stats: Dict, box_score: Dict) -> Optional[Dict[str, Any]]:
        """Extract batting statistics for a player"""
        try:
            player_id = str(player_stats.get('personId', ''))
            
            # Get player name from roster data
            player_name = self._get_player_name(player_id, box_score)
            
            # Convert string values to integers, handling empty strings
            def safe_int(value):
                try:
                    return int(value) if value and value != '' else 0
                except (ValueError, TypeError):
                    return 0
            
            # Get batting order and position
            batting_order = player_stats.get('battingOrder', '')
            position = player_stats.get('position', '')  # Position is a direct string in this API response
            substitution = bool(player_stats.get('substitution', False))
            
            # Convert batting order to number (1-9) for starters
            try:
                # MLB API uses string like '100' for 1st, '200' for 2nd, etc.
                order_num = int(batting_order[0]) if batting_order and not substitution else None
            except (ValueError, IndexError):
                order_num = None
                
            return {
                'order': order_num,
                'player_id': player_id,
                'name': player_name,
                'position': position,
                'sub': substitution,
                'at_bats': safe_int(player_stats.get('ab', 0)),
                'hits': safe_int(player_stats.get('h', 0)),
                'runs': safe_int(player_stats.get('r', 0)),
                'rbis': safe_int(player_stats.get('rbi', 0)),
                'doubles': safe_int(player_stats.get('doubles', 0)),
                'triples': safe_int(player_stats.get('triples', 0)),
                'home_runs': safe_int(player_stats.get('hr', 0)),
                'walks': safe_int(player_stats.get('bb', 0)),
                'strikeouts': safe_int(player_stats.get('k', 0)),
                'stolen_bases': safe_int(player_stats.get('sb', 0)),
                'caught_stealing': 0  # Not available in this format
            }
        except Exception as e:
            print(f"Error extracting batting stats: {e}")
            return None
    
    def _extract_pitching_stats(self, player_stats: Dict, box_score: Dict) -> Optional[Dict[str, Any]]:
        """Extract pitching statistics for a player"""
        try:
            player_id = str(player_stats.get('personId', ''))
            
            # Get player name from roster data
            player_name = self._get_player_name(player_id, box_score)
            
            # Convert string values to appropriate types, handling empty strings
            def safe_int(value):
                try:
                    return int(value) if value and value != '' else 0
                except (ValueError, TypeError):
                    return 0
            
            def safe_float(value):
                try:
                    return float(value) if value and value != '' else 0.0
                except (ValueError, TypeError):
                    return 0.0
            
            def parse_innings(innings_str):
                """Parse baseball innings notation (e.g., '6.1' = 6⅓ innings)"""
                try:
                    if not innings_str or innings_str == '':
                        return 0.0
                    
                    innings_str = str(innings_str)
                    if '.' in innings_str:
                        whole, fraction = innings_str.split('.')
                        whole_innings = int(whole) if whole else 0
                        
                        # Convert baseball fractional notation to decimal
                        if fraction == '1':
                            fraction_decimal = 1/3  # 1 out = 1/3 inning
                        elif fraction == '2':
                            fraction_decimal = 2/3  # 2 outs = 2/3 inning
                        else:
                            # Handle other cases (shouldn't happen in baseball)
                            fraction_decimal = int(fraction) / 3 if fraction.isdigit() else 0
                        
                        return whole_innings + fraction_decimal
                    else:
                        return float(innings_str)
                except (ValueError, TypeError):
                    return 0.0
            
            # Parse wins/losses from namefield (e.g., "Lodolo  (W, 9-8)")
            wins = 0
            losses = 0
            saves = 0
            namefield = player_stats.get('namefield', '')
            if '(W,' in namefield:
                wins = 1
            elif '(L,' in namefield:
                losses = 1
            elif '(S,' in namefield:
                saves = 1
            
            return {
                'player_id': player_id,
                'name': player_name,
                'wins': wins,
                'losses': losses,
                'saves': saves,
                'innings_pitched': parse_innings(player_stats.get('ip', 0)),
                'hits_allowed': safe_int(player_stats.get('h', 0)),
                'runs_allowed': safe_int(player_stats.get('r', 0)),
                'earned_runs': safe_int(player_stats.get('er', 0)),
                'walks_allowed': safe_int(player_stats.get('bb', 0)),
                'strikeouts': safe_int(player_stats.get('k', 0)),
                'home_runs_allowed': safe_int(player_stats.get('hr', 0)),
                'pitches_thrown': safe_int(player_stats.get('p', 0))
            }
        except Exception as e:
            print(f"Error extracting pitching stats: {e}")
            return None
    
    def _get_player_name(self, player_id: str, box_score: Dict) -> str:
        """Get player name from box score data"""
        try:
            # Look in player info section using the correct key format
            if 'playerInfo' in box_score:
                player_key = f'ID{player_id}'
                if player_key in box_score['playerInfo']:
                    player_info = box_score['playerInfo'][player_key]
                    return player_info.get('fullName', f'Player {player_id}')
            
            # Fallback to generic name
            return f'Player {player_id}'
            
        except Exception as e:
            print(f"Error getting player name: {e}")
            return f'Player {player_id}'
    
    def get_player_info(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed player information"""
        try:
            player_data = statsapi.get('person', {'personId': player_id})
            
            if player_data and 'people' in player_data and len(player_data['people']) > 0:
                player = player_data['people'][0]
                return {
                    'id': player.get('id'),
                    'fullName': player.get('fullName', ''),
                    'firstName': player.get('firstName', ''),
                    'lastName': player.get('lastName', ''),
                    'position': player.get('primaryPosition', {}).get('name', ''),
                    'jersey_number': player.get('primaryNumber', ''),
                    'team': player.get('currentTeam', {}).get('name', ''),
                    'birthDate': player.get('birthDate', ''),
                    'height': player.get('height', ''),
                    'weight': player.get('weight', ''),
                    'bats': player.get('batSide', {}).get('description', ''),
                    'throws': player.get('pitchHand', {}).get('description', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching player info: {e}")
            return None
        
    def get_game_options(self, home_team_id: int, away_team_id: int, game_date: str) -> List[Dict[str, Any]]:
        """Get available game options for a given date and teams (for doubleheader selection)"""
        try:
            self._rate_limit()
            
            # Convert date to string format
            if hasattr(game_date, 'strftime'):
                date_str = game_date.strftime('%Y-%m-%d')
            else:
                date_str = str(game_date)
            
            # Get schedule for the date
            schedule = statsapi.schedule(date=date_str)
            
            # Find all matching games
            matching_games = [
                game for game in schedule
                if game.get('home_id') == home_team_id and game.get('away_id') == away_team_id
            ]
            
            if not matching_games:
                return []
            
            game_options = []
            for idx, game in enumerate(matching_games):
                # Get actual date if available
                game_datetime = game.get('game_datetime')
                actual_date = date_str
                game_time = "Unknown Time"
                
                if game_datetime:
                    try:
                        dt = datetime.strptime(game_datetime, "%Y-%m-%dT%H:%M:%SZ")
                        actual_date = dt.strftime("%Y-%m-%d")
                        game_time = dt.strftime("%I:%M %p")
                    except:
                        pass
                
                # Create descriptive option
                game_num = game.get('game_num', idx + 1)
                status = game.get('status', 'Unknown')
                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)
                
                description = f"Game {game_num}"
                if len(matching_games) > 1:
                    description += f" of {len(matching_games)}"
                
                description += f" - {game_time}"
                
                if status in ['Final', 'Completed']:
                    description += f" - {game.get('away_name', 'Away')} {away_score}, {game.get('home_name', 'Home')} {home_score}"
                else:
                    description += f" - {status}"
                
                if actual_date != date_str:
                    description += f" (played on {actual_date})"
                
                game_options.append({
                    'index': idx,
                    'description': description,
                    'game_id': game.get('game_id'),
                    'actual_date': actual_date,
                    'status': status,
                    'home_score': home_score,
                    'away_score': away_score,
                    'game_time': game_time
                })
            
            return game_options
            
        except Exception as e:
            print(f"Error getting game options: {e}")
            return []

    # Additional method to ensure it's available
    def get_doubleheader_options(self, home_team_id: int, away_team_id: int, game_date: str) -> List[Dict[str, Any]]:
        """Alternative method name for getting game options"""
        return self.get_game_options(home_team_id, away_team_id, game_date)
