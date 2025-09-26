import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from data_manager import DataManager
from stats_calculator import StatsCalculator
from mlb_api_client import MLBApiClient

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'stats_calculator' not in st.session_state:
    st.session_state.stats_calculator = StatsCalculator()
if 'mlb_client' not in st.session_state:
    st.session_state.mlb_client = MLBApiClient()

def main():
    st.set_page_config(
        page_title="Baseball Statistics Aggregator",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("⚾ Baseball Statistics Aggregator")
    st.markdown("Track and analyze player statistics from MLB games you've attended")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Add Game", "My Games", "Player Stats", "Dashboard", "Export Data"]
    )
    
    if page == "Add Game":
        add_game_page()
    elif page == "My Games":
        my_games_page()
    elif page == "Player Stats":
        player_stats_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "Export Data":
        export_data_page()

def add_game_page():
    st.header("Add New Game")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get list of MLB teams
        teams = st.session_state.mlb_client.get_teams()
        if teams:
            team_options = {f"{team['name']} ({team['abbreviation']})": team['id'] for team in teams}
            
            home_team = st.selectbox(
                "Home Team",
                options=list(team_options.keys()),
                help="Select the home team"
            )
            
            away_team = st.selectbox(
                "Away Team", 
                options=list(team_options.keys()),
                help="Select the away team"
            )
        else:
            st.error("Unable to load team data. Please check your connection.")
            return
    
    with col2:
        game_date = st.date_input(
            "Game Date",
            value=date.today(),
            max_value=date.today(),
            help="Select the date of the game you attended"
        )
        
        notes = st.text_area(
            "Notes (Optional)",
            placeholder="Add any notes about the game..."
        )
    
    if st.button("Add Game", type="primary"):
        if home_team and away_team and game_date:
            if home_team == away_team:
                st.error("Home and away teams cannot be the same!")
                return
            
            home_team_id = team_options[home_team]
            away_team_id = team_options[away_team]
            
            with st.spinner("Fetching game data from MLB API..."):
                game_data = st.session_state.mlb_client.get_game_data(
                    home_team_id, away_team_id, game_date
                )
            
            if game_data:
                # Save the game
                success = st.session_state.data_manager.add_game(
                    game_data, notes
                )
                
                if success:
                    st.success("Game added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save game data.")
            else:
                st.error("No game found for the selected teams and date. Please verify the details.")

def my_games_page():
    st.header("My Attended Games")
    
    games = st.session_state.data_manager.get_all_games()
    
    if not games:
        st.info("No games added yet. Go to 'Add Game' to start tracking your attended games.")
        return
    
    # Display games in a table format
    game_list = []
    for game in games:
        game_info = {
            "Date": game.get('date', 'N/A'),
            "Home Team": game.get('home_team', 'N/A'),
            "Away Team": game.get('away_team', 'N/A'),
            "Score": f"{game.get('away_score', 0)} - {game.get('home_score', 0)}",
            "Notes": game.get('notes', '')
        }
        game_list.append(game_info)
    
    df = pd.DataFrame(game_list)
    st.dataframe(df, use_container_width=True)
    
    # Game details section
    if st.checkbox("Show detailed game information"):
        selected_game_idx = st.selectbox(
            "Select a game to view details",
            range(len(games)),
            format_func=lambda x: f"{games[x].get('date')} - {games[x].get('away_team')} @ {games[x].get('home_team')}"
        )
        
        if selected_game_idx is not None:
            game = games[selected_game_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Game Summary")
                st.write(f"**Date:** {game.get('date')}")
                st.write(f"**Teams:** {game.get('away_team')} @ {game.get('home_team')}")
                st.write(f"**Final Score:** {game.get('away_score')} - {game.get('home_score')}")
                if game.get('notes'):
                    st.write(f"**Notes:** {game.get('notes')}")
            
            with col2:
                if st.button("Remove Game", type="secondary"):
                    if st.session_state.data_manager.remove_game(selected_game_idx):
                        st.success("Game removed successfully!")
                        st.rerun()

def player_stats_page():
    st.header("Player Statistics")
    
    games = st.session_state.data_manager.get_all_games()
    
    if not games:
        st.info("No games added yet. Add some games to see player statistics.")
        return
    
    # Calculate aggregated stats
    batting_stats, pitching_stats = st.session_state.stats_calculator.calculate_aggregate_stats(games)
    
    tab1, tab2 = st.tabs(["Batting Stats", "Pitching Stats"])
    
    with tab1:
        if batting_stats:
            st.subheader("Batting Statistics")
            
            # Convert to DataFrame for better display
            batting_df = pd.DataFrame(batting_stats)
            
            # Sort by games played
            if 'games' in batting_df.columns:
                batting_df = batting_df.sort_values('games', ascending=False)
            
            # Display top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Players Seen", len(batting_df))
                if 'at_bats' in batting_df.columns:
                    total_at_bats = batting_df['at_bats'].sum()
                    st.metric("Total At Bats", total_at_bats)
            
            with col2:
                if 'hits' in batting_df.columns:
                    total_hits = batting_df['hits'].sum()
                    st.metric("Total Hits", total_hits)
                if 'home_runs' in batting_df.columns:
                    total_hrs = batting_df['home_runs'].sum()
                    st.metric("Total Home Runs", total_hrs)
            
            # Filter options
            min_games = st.slider("Minimum games played", 1, max(1, batting_df['games'].max() if 'games' in batting_df.columns else 1), 1)
            filtered_batting = batting_df[batting_df['games'] >= min_games] if 'games' in batting_df.columns else batting_df
            
            st.dataframe(filtered_batting, use_container_width=True)
        else:
            st.info("No batting statistics available.")
    
    with tab2:
        if pitching_stats:
            st.subheader("Pitching Statistics")
            
            # Convert to DataFrame for better display
            pitching_df = pd.DataFrame(pitching_stats)
            
            # Sort by games played
            if 'games' in pitching_df.columns:
                pitching_df = pitching_df.sort_values('games', ascending=False)
            
            # Display summary stats
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Pitchers Seen", len(pitching_df))
                if 'innings_pitched' in pitching_df.columns:
                    total_ip = pitching_df['innings_pitched'].sum()
                    st.metric("Total Innings Pitched", f"{total_ip:.1f}")
            
            with col2:
                if 'strikeouts' in pitching_df.columns:
                    total_ks = pitching_df['strikeouts'].sum()
                    st.metric("Total Strikeouts", total_ks)
                if 'earned_runs' in pitching_df.columns:
                    total_er = pitching_df['earned_runs'].sum()
                    st.metric("Total Earned Runs", total_er)
            
            # Filter options
            min_games = st.slider("Minimum games pitched", 1, max(1, pitching_df['games'].max() if 'games' in pitching_df.columns else 1), 1, key="pitching_filter")
            filtered_pitching = pitching_df[pitching_df['games'] >= min_games] if 'games' in pitching_df.columns else pitching_df
            
            st.dataframe(filtered_pitching, use_container_width=True)
        else:
            st.info("No pitching statistics available.")

def dashboard_page():
    st.header("Statistics Dashboard")
    
    games = st.session_state.data_manager.get_all_games()
    
    if not games:
        st.info("No games added yet. Add some games to see visualizations.")
        return
    
    # Calculate stats for visualization
    batting_stats, pitching_stats = st.session_state.stats_calculator.calculate_aggregate_stats(games)
    
    # Games over time
    st.subheader("Games Attended Over Time")
    
    game_dates = [datetime.strptime(game['date'], '%Y-%m-%d') for game in games]
    games_df = pd.DataFrame({'date': game_dates})
    games_df['count'] = 1
    games_df = games_df.groupby('date').sum().reset_index()
    
    fig_games = px.line(games_df, x='date', y='count', 
                       title='Games Attended Over Time',
                       labels={'count': 'Number of Games', 'date': 'Date'})
    st.plotly_chart(fig_games, use_container_width=True)
    
    # Team frequency
    st.subheader("Teams Seen Most Often")
    
    team_counts = {}
    for game in games:
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        team_counts[home_team] = team_counts.get(home_team, 0) + 1
        team_counts[away_team] = team_counts.get(away_team, 0) + 1
    
    if team_counts:
        teams_df = pd.DataFrame(list(team_counts.items()), columns=['Team', 'Games'])
        teams_df = teams_df.sort_values('Games', ascending=True).tail(10)
        
        fig_teams = px.bar(teams_df, x='Games', y='Team', orientation='h',
                          title='Top 10 Teams by Games Attended')
        st.plotly_chart(fig_teams, use_container_width=True)
    
    # Player performance charts
    if batting_stats:
        st.subheader("Top Batting Performances")
        
        batting_df = pd.DataFrame(batting_stats)
        
        if len(batting_df) > 0 and 'games' in batting_df.columns:
            # Filter for players with multiple games
            multi_game_players = batting_df[batting_df['games'] > 1]
            
            if len(multi_game_players) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'batting_average' in multi_game_players.columns:
                        top_avg = multi_game_players.nlargest(10, 'batting_average')
                        fig_avg = px.bar(top_avg, x='batting_average', y='player_name',
                                        orientation='h', title='Top 10 Batting Averages')
                        st.plotly_chart(fig_avg, use_container_width=True)
                
                with col2:
                    if 'home_runs' in multi_game_players.columns:
                        top_hr = multi_game_players.nlargest(10, 'home_runs')
                        fig_hr = px.bar(top_hr, x='home_runs', y='player_name',
                                       orientation='h', title='Top 10 Home Run Totals')
                        st.plotly_chart(fig_hr, use_container_width=True)

def export_data_page():
    st.header("Export Data")
    
    games = st.session_state.data_manager.get_all_games()
    
    if not games:
        st.info("No data to export. Add some games first.")
        return
    
    st.write("Export your personal baseball statistics database in various formats.")
    
    export_format = st.selectbox(
        "Select export format",
        ["JSON", "CSV"]
    )
    
    if st.button("Generate Export", type="primary"):
        try:
            if export_format == "JSON":
                # Export complete data as JSON
                export_data = {
                    "games": games,
                    "export_date": datetime.now().isoformat(),
                    "total_games": len(games)
                }
                
                json_str = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"baseball_stats_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
                
            elif export_format == "CSV":
                # Export games as CSV
                game_list = []
                for game in games:
                    game_info = {
                        "date": game.get('date', ''),
                        "home_team": game.get('home_team', ''),
                        "away_team": game.get('away_team', ''),
                        "home_score": game.get('home_score', ''),
                        "away_score": game.get('away_score', ''),
                        "notes": game.get('notes', '')
                    }
                    game_list.append(game_info)
                
                df = pd.DataFrame(game_list)
                csv_str = df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv_str,
                    file_name=f"baseball_games_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error generating export: {str(e)}")
    
    # Display summary statistics
    st.subheader("Export Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Games", len(games))
    
    with col2:
        unique_teams = set()
        for game in games:
            unique_teams.add(game.get('home_team', ''))
            unique_teams.add(game.get('away_team', ''))
        unique_teams.discard('')
        st.metric("Unique Teams", len(unique_teams))
    
    with col3:
        if games:
            date_range = []
            for game in games:
                try:
                    date_range.append(datetime.strptime(game.get('date', ''), '%Y-%m-%d'))
                except:
                    continue
            
            if date_range:
                days_span = (max(date_range) - min(date_range)).days
                st.metric("Date Range (Days)", days_span)

if __name__ == "__main__":
    main()
