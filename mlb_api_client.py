import statsapi
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class MLBApiClient:
    def __init__(self):
        self.teams_cache = None
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get list of all MLB teams"""
        if self.teams_cache is not None:
            return self.teams_cache
        
        try:
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
            self.teams_cache = teams
            return teams
            
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def get_game_data(self, home_team_id: int, away_team_id: int, game_date: str) -> Optional[Dict[str, Any]]:
        """Get game data for specific teams and date"""
        try:
            # Convert date to string format if it's a date object
            if hasattr(game_date, 'strftime'):
                date_str = game_date.strftime('%Y-%m-%d')
            else:
                date_str = str(game_date)
            
            # Get schedule for the date
            schedule = statsapi.schedule(date=date_str)
            
            target_game = None
            for game in schedule:
                if (game.get('home_id') == home_team_id and 
                    game.get('away_id') == away_team_id):
                    target_game = game
                    break
            
            if not target_game:
                return None
            
            game_id = target_game.get('game_id')
            if not game_id:
                return None
            
            # Get detailed box score
            box_score = statsapi.boxscore_data(game_id)
            
            # Extract game information
            game_data = {
                'game_id': game_id,
                'date': date_str,
                'home_team': target_game.get('home_name', ''),
                'away_team': target_game.get('away_name', ''),
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'home_score': target_game.get('home_score', 0),
                'away_score': target_game.get('away_score', 0),
                'game_status': target_game.get('status', ''),
                'venue': target_game.get('venue_name', ''),
                'home_team_batting': [],
                'away_team_batting': [],
                'home_team_pitching': [],
                'away_team_pitching': []
            }
            
            # Extract batting statistics
            if 'teamStats' in box_score:
                home_stats = box_score['teamStats'].get('home', {})
                away_stats = box_score['teamStats'].get('away', {})
                
                # Process home team batting
                if 'batting' in home_stats:
                    for player_id, player_stats in home_stats['batting'].items():
                        if player_id.isdigit():  # Skip team totals
                            batting_data = self._extract_batting_stats(player_stats, box_score)
                            if batting_data:
                                game_data['home_team_batting'].append(batting_data)
                
                # Process away team batting
                if 'batting' in away_stats:
                    for player_id, player_stats in away_stats['batting'].items():
                        if player_id.isdigit():  # Skip team totals
                            batting_data = self._extract_batting_stats(player_stats, box_score)
                            if batting_data:
                                game_data['away_team_batting'].append(batting_data)
                
                # Process home team pitching
                if 'pitching' in home_stats:
                    for player_id, player_stats in home_stats['pitching'].items():
                        if player_id.isdigit():  # Skip team totals
                            pitching_data = self._extract_pitching_stats(player_stats, box_score)
                            if pitching_data:
                                game_data['home_team_pitching'].append(pitching_data)
                
                # Process away team pitching
                if 'pitching' in away_stats:
                    for player_id, player_stats in away_stats['pitching'].items():
                        if player_id.isdigit():  # Skip team totals
                            pitching_data = self._extract_pitching_stats(player_stats, box_score)
                            if pitching_data:
                                game_data['away_team_pitching'].append(pitching_data)
            
            return game_data
            
        except Exception as e:
            print(f"Error fetching game data: {e}")
            return None
    
    def _extract_batting_stats(self, player_stats: Dict, box_score: Dict) -> Optional[Dict[str, Any]]:
        """Extract batting statistics for a player"""
        try:
            player_id = str(player_stats.get('personId', ''))
            
            # Get player name from roster data
            player_name = self._get_player_name(player_id, box_score)
            
            return {
                'player_id': player_id,
                'name': player_name,
                'at_bats': player_stats.get('atBats', 0),
                'hits': player_stats.get('hits', 0),
                'runs': player_stats.get('runs', 0),
                'rbis': player_stats.get('rbi', 0),
                'doubles': player_stats.get('doubles', 0),
                'triples': player_stats.get('triples', 0),
                'home_runs': player_stats.get('homeRuns', 0),
                'walks': player_stats.get('baseOnBalls', 0),
                'strikeouts': player_stats.get('strikeOuts', 0),
                'stolen_bases': player_stats.get('stolenBases', 0),
                'caught_stealing': player_stats.get('caughtStealing', 0)
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
            
            return {
                'player_id': player_id,
                'name': player_name,
                'wins': player_stats.get('wins', 0),
                'losses': player_stats.get('losses', 0),
                'saves': player_stats.get('saves', 0),
                'innings_pitched': float(player_stats.get('inningsPitched', 0)),
                'hits_allowed': player_stats.get('hits', 0),
                'runs_allowed': player_stats.get('runs', 0),
                'earned_runs': player_stats.get('earnedRuns', 0),
                'walks_allowed': player_stats.get('baseOnBalls', 0),
                'strikeouts': player_stats.get('strikeOuts', 0),
                'home_runs_allowed': player_stats.get('homeRuns', 0),
                'pitches_thrown': player_stats.get('numberOfPitches', 0)
            }
        except Exception as e:
            print(f"Error extracting pitching stats: {e}")
            return None
    
    def _get_player_name(self, player_id: str, box_score: Dict) -> str:
        """Get player name from box score data"""
        try:
            # Look in player info section
            if 'playerInfo' in box_score:
                for player_info in box_score['playerInfo']:
                    if str(player_info.get('id', '')) == player_id:
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
