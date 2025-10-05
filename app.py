import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
import time
from data_manager import DataManager
from stats_calculator import StatsCalculator
from mlb_api_client import MLBApiClient
from auth_manager import AuthManager

def format_game_display_name(game):
    """Create a descriptive display name for games, including doubleheader info"""
    base_name = f"{game.get('date')} - {game.get('away_team')} @ {game.get('home_team')}"
    
    # Add score info
    base_name += f" ({game.get('away_score')}-{game.get('home_score')})"
    
    # Add doubleheader info if applicable
    if game.get('is_doubleheader') and game.get('game_number'):
        base_name += f" - Game {game.get('game_number')}"
    elif game.get('game_number'):
        base_name += f" - Game {game.get('game_number')}"
    
    return base_name

def main():
    st.set_page_config(
        page_title="Baseball Statistics Aggregator",
        page_icon="⚾",
        layout="wide"
    )

    # Initialize authentication manager
    auth_manager = AuthManager()
    
    # Check if user is authenticated
    if auth_manager.check_authentication():
        # Welcome message
        current_user = auth_manager.get_current_user()
        display_name = auth_manager.get_user_display_name() or current_user
        st.success(f"Welcome back, {display_name}! 🎉")
        
        # Show main application
        show_main_app(auth_manager)
        
    else:
        # User is not authenticated, handle login/registration
        st.title("⚾ Baseball Statistics Aggregator")
        st.markdown("### 🔐 Please log in to continue")
        
        # Create tabs for login and registration
        login_tab, register_tab = st.tabs(["🔑 Login", "📝 Register"])
        
        with login_tab:
            st.markdown("#### Log in to your account")
            
            # Call login - this will show the form and handle authentication
            login_result = auth_manager.login()
            
            if login_result[0] is True:  # Successfully logged in
                st.success("✅ Login successful!")
                st.balloons()
                st.rerun()  # Refresh to show main app
            elif login_result[0] is False:  # Login failed
                st.error("❌ Invalid username or password")
        
        with register_tab:
            st.markdown("#### Create a new account")
            show_registration_form(auth_manager)

def show_registration_form(auth_manager):
    """Show the registration form"""
    with st.form("register_form"):
        new_username = st.text_input("Username", placeholder="Choose a unique username")
        new_name = st.text_input("Full Name", placeholder="Your full name")
        new_email = st.text_input("Email", placeholder="your.email@example.com")
        new_password = st.text_input("Password", type="password", placeholder="Create a secure password")
        submitted = st.form_submit_button("🚀 Create Account")
        if submitted and new_username and new_name and new_email and new_password:
            if auth_manager.register_user(new_username, new_name, new_password, new_email):
                st.success("🎉 Registration successful! Please log in with your new credentials.")
            else:
                st.error("❌ Username already exists or registration failed. Please try a different username.")
        elif submitted:
            st.warning("⚠️ Please fill in all fields.")

def show_main_app(auth_manager):
        user = auth_manager.get_current_user()
        user_display = auth_manager.get_user_display_name() or user

        # Initialize user-specific session state
        if 'data_manager' not in st.session_state or st.session_state.data_manager.user_id != user:
            st.session_state.data_manager = DataManager(user_id=user)
        if 'stats_calculator' not in st.session_state:
            st.session_state.stats_calculator = StatsCalculator()
        if 'mlb_client' not in st.session_state:
            st.session_state.mlb_client = MLBApiClient()

        # Sidebar with user info and logout
        st.sidebar.markdown("### 👤 User Information")
        st.sidebar.info(f"**Logged in as:** {user_display}")
        st.sidebar.markdown("---")
        
        # Logout button in sidebar
        if st.sidebar.button("🚪 Logout", type="secondary"):
            auth_manager.logout()
            st.success("👋 You have been logged out successfully!")
            time.sleep(1)
            st.rerun()

        st.title("⚾ Baseball Statistics Aggregator")
        st.markdown(f"**Welcome back, {user_display}!** 🎉 Track and analyze your MLB game attendance.")

        # Sidebar navigation
        if 'page' not in st.session_state:
            st.session_state.page = "Add Game"

        pages = ["Add Game", "My Games", "Player Stats", "Dashboard", "Export Data"]
        for p in pages:
            if st.sidebar.button(p, use_container_width=True):
                st.session_state.page = p
                st.rerun()

        page = st.session_state.page

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
    
    # Add some helpful information
    with st.expander("ℹ️ How to Add a Game"):
        st.write("""
        1. Select the home and away teams from the dropdown menus
        2. Choose the date you attended the game
        3. Optionally add notes about your experience
        4. Click 'Add Game' to fetch the official MLB statistics
        
        **Note:** Only completed games can be added to ensure accurate statistics.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get list of MLB teams with error handling
        with st.spinner("Loading MLB teams..."):
            teams = st.session_state.mlb_client.get_teams()
            
        if teams:
            team_options = {f"{team['name']} ({team['abbreviation']})": team['id'] for team in teams}
            
            home_team = st.selectbox(
                "🏠 Home Team",
                options=list(team_options.keys()),
                help="Select the home team",
                key="home_team_select"
            )
            
            away_team = st.selectbox(
                "✈️ Away Team", 
                options=list(team_options.keys()),
                help="Select the away team",
                key="away_team_select"
            )
            
            # Show a warning if same team is selected
            if home_team and away_team and home_team == away_team:
                st.warning("⚠️ Home and away teams cannot be the same!")
                
        else:
            st.error("❌ Unable to load team data. Please refresh the page or check your internet connection.")
            if st.button("🔄 Retry Loading Teams"):
                st.rerun()
            return
    
    with col2:
        game_date = st.date_input(
            "📅 Game Date",
            value=date.today(),
            max_value=date.today(),
            help="Select the date of the game you attended",
            key="game_date_input"
        )
        
        notes = st.text_area(
            "📝 Notes (Optional)",
            placeholder="Add any notes about the game (e.g., weather, highlights, seat location)...",
            height=100,
            key="game_notes_input"
        )
    
    # Add validation and better user feedback
    can_add_game = home_team and away_team and game_date and home_team != away_team
    
    if st.button("⚾ Add Game", type="primary", disabled=not can_add_game):
        if not can_add_game:
            st.error("Please select different home and away teams and a valid date.")
            return
            
        home_team_id = team_options[home_team]
        away_team_id = team_options[away_team]
        
        # First check if multiple games exist
        try:
            game_options = st.session_state.mlb_client.get_game_options(
                home_team_id, away_team_id, game_date
            )
        except AttributeError:
            # Fallback if method doesn't exist (shouldn't happen now)
            st.warning("Using fallback method for game detection...")
            game_data = st.session_state.mlb_client.get_game_data(
                home_team_id, away_team_id, game_date
            )
            if game_data and game_data.get('multiple_games'):
                game_options = game_data['multiple_games']
            else:
                game_options = []
        except Exception as e:
            st.error(f"Error getting game options: {e}")
            game_options = []
        
        if len(game_options) > 1:
            # Store game options in session state for selection
            st.session_state.game_options = game_options
            st.session_state.pending_teams = (home_team_id, away_team_id, game_date, notes)
            st.rerun()
        else:
            # Single game - fetch directly
            game_data = st.session_state.mlb_client.get_game_data(
                home_team_id, away_team_id, game_date
            )
            if game_data:
                st.session_state.selected_game_data = game_data
                st.session_state.pending_notes = notes
                st.rerun()
    
    # Handle multiple game selection
    if hasattr(st.session_state, 'game_options') and st.session_state.game_options:
        st.info(f"🔄 Found {len(st.session_state.game_options)} games for this matchup!")
        
        selected_game = st.selectbox(
            "Select which game to add:",
            range(len(st.session_state.game_options)),
            format_func=lambda x: st.session_state.game_options[x]['description'],
            key="game_selection"
        )
        
        if st.button("📥 Fetch Selected Game", type="secondary"):
            home_team_id, away_team_id, game_date, notes = st.session_state.pending_teams
            game_data = st.session_state.mlb_client.get_game_data(
                home_team_id, away_team_id, game_date, game_selection=selected_game
            )
            if game_data:
                st.session_state.selected_game_data = game_data
                st.session_state.pending_notes = notes
                # Clear game options
                delattr(st.session_state, 'game_options')
                delattr(st.session_state, 'pending_teams')
                st.rerun()

    # Display game data if available
    if hasattr(st.session_state, 'selected_game_data') and st.session_state.selected_game_data:
        game_data = st.session_state.selected_game_data
        notes = getattr(st.session_state, 'pending_notes', '')
        
        # Show game preview before saving
        with st.expander("🎯 Game Preview", expanded=True):
            col_preview1, col_preview2 = st.columns(2)
            with col_preview1:
                st.write(f"**Date:** {game_data.get('date')}")
                st.write(f"**Venue:** {game_data.get('venue', 'N/A')}")
                st.write(f"**Status:** {game_data.get('game_status', 'N/A')}")
                if game_data.get('is_doubleheader'):
                    st.write(f"**Game:** {game_data.get('game_number', 1)} of {game_data.get('total_games_found', 2)}")
            with col_preview2:
                st.write(f"**Final Score:**")
                st.write(f"{game_data.get('away_team')} **{game_data.get('away_score')}** @ {game_data.get('home_team')} **{game_data.get('home_score')}**")
                
                # Show some basic stats
                total_batters = len(game_data.get('home_team_batting', [])) + len(game_data.get('away_team_batting', []))
                total_pitchers = len(game_data.get('home_team_pitching', [])) + len(game_data.get('away_team_pitching', []))
                st.write(f"**Players:** {total_batters} batters, {total_pitchers} pitchers")
        
        # Confirm save
        if st.button("💾 Confirm & Save Game", type="secondary"):
            with st.spinner("Saving game data..."):
                success = st.session_state.data_manager.add_game(game_data, notes)
                
            if success:
                st.success("🎉 Game added successfully!")
                st.balloons()
                # Clear the cached game data
                if hasattr(st.session_state, 'selected_game_data'):
                    delattr(st.session_state, 'selected_game_data')
                if hasattr(st.session_state, 'pending_notes'):
                    delattr(st.session_state, 'pending_notes')
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to save game data. Please try again.")

def my_games_page():
    st.header("My Attended Games")
    games = st.session_state.data_manager.get_all_games()
    if not games:
        st.info("No games added yet. Go to 'Add Game' to start tracking your attended games.")
        return

    # Sort games in reverse chronological order (most recent first)
    games.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Detect Streamlit theme (dark/light)
    theme = st.get_option("theme.base")
    is_dark = theme == "dark"
    card_bg = "#23272f" if is_dark else "#f8f9fa"
    card_text = "#f8f9fa" if is_dark else "#23272f"
    card_shadow = "0 2px 8px rgba(0,0,0,0.18)" if is_dark else "0 2px 8px rgba(0,0,0,0.04)"

    cols = st.columns(3)

    for idx, game in enumerate(games):
        with cols[idx % 3]:
            home_team = game.get('home_team', 'N/A')
            away_team = game.get('away_team', 'N/A')
            home_score = game.get('home_score', 'N/A')
            away_score = game.get('away_score', 'N/A')
            date_str = game.get('date', 'N/A')
            notes = game.get('notes', '')

            st.markdown(f"""
            <div style='background: {card_bg}; color: {card_text}; border-radius: 12px; padding: 1em 1.2em; margin-bottom: 1.2em; box-shadow: {card_shadow};'>
                <h4 style='margin-bottom:0.2em;'>📅 {date_str}</h4>
                <div style='font-size:1.1em; margin-bottom:0.5em;'>
                    <div style='font-weight:600; margin-bottom:0.2em;'>{away_team} <span style='color:#888;'>({away_score})</span></div>
                    <div style='color:#666; margin-bottom:0.2em;'>@</div>
                    <div style='font-weight:600;'>{home_team} <span style='color:#888;'>({home_score})</span></div>
                </div>
                {f'<div style="margin-bottom:0.5em; color:#bbb;">📝 {notes}</div>' if notes else ''}
            </div>
            """, unsafe_allow_html=True)
            # Working remove button below the card
            remove_btn_label = f"Remove Game {idx+1} ({away_team} @ {home_team})"
            if st.button("🗑️ Remove Game", key=f"remove_game_{idx}"):
                # Remove game using its unique properties instead of index
                try:
                    # Check if the new method exists, fallback to old method if not
                    if hasattr(st.session_state.data_manager, 'remove_game_by_properties'):
                        success = st.session_state.data_manager.remove_game_by_properties(
                            game.get('date'), 
                            game.get('home_team_id'), 
                            game.get('away_team_id'),
                            game.get('game_number')
                        )
                    else:
                        # Fallback: find the original index in the unsorted list
                        all_games = st.session_state.data_manager.get_all_games()
                        original_idx = None
                        for orig_idx, orig_game in enumerate(all_games):
                            if (orig_game.get('date') == game.get('date') and
                                str(orig_game.get('home_team_id')) == str(game.get('home_team_id')) and
                                str(orig_game.get('away_team_id')) == str(game.get('away_team_id')) and
                                str(orig_game.get('game_number')) == str(game.get('game_number'))):
                                original_idx = orig_idx
                                break
                        
                        if original_idx is not None:
                            success = st.session_state.data_manager.remove_game(original_idx)
                        else:
                            success = False
                    
                    if success:
                        st.success("Game removed successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to remove game. Please try again.")
                except Exception as e:
                    st.error(f"Error removing game: {str(e)}")
                    print(f"Error in remove game button: {e}")

    # Optionally, keep the detailed info section if needed
    if st.checkbox("Show detailed game information"):
        selected_game_idx = st.selectbox(
            "Select a game to view details",
            range(len(games)),
            format_func=lambda x: format_game_display_name(games[x])
        )
        if selected_game_idx is not None:
            game = games[selected_game_idx]
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Game Summary")
                st.write(f"**Date:** {game.get('date')}")
                st.write(f"**Teams:** {game.get('away_team')} @ {game.get('home_team')}")
                st.write(f"**Final Score:** {game.get('away_score')} - {game.get('home_score')}")
                
                # Show doubleheader information
                if game.get('is_doubleheader'):
                    st.write(f"**Doubleheader:** Game {game.get('game_number', 'N/A')} of {game.get('total_games_found', 2)}")
                elif game.get('game_number'):
                    st.write(f"**Game Number:** {game.get('game_number')}")
                
                if game.get('venue'):
                    st.write(f"**Venue:** {game.get('venue')}")
                
                if game.get('notes'):
                    st.write(f"**Notes:** {game.get('notes')}")
                # Display box score data
                if game:
                    st.markdown("### Box Score")
                    tabs = st.tabs(["Batting", "Pitching", "Game Info"])
                    
                    with tabs[0]:  # Batting Stats
                        # Display away team batting
                            st.markdown("#### Away Team Batting")
                            away_batting = None
                            
                            # Get away team batting stats
                            away_batting_data = game.get('away_team_batting', [])
                            
                            if away_batting_data:
                                # Create DataFrame and sort by batting order
                                away_batting = pd.DataFrame(away_batting_data)
                                
                                # Ensure required columns exist before processing
                                required_columns = ['name', 'order', 'sub', 'position']
                                for col in required_columns:
                                    if col not in away_batting.columns:
                                        away_batting[col] = None
                                
                                # Format player names with indentation for substitutes
                                def format_player_name(row):
                                    try:
                                        name = str(row['name']) if pd.notnull(row['name']) else 'Unknown'
                                        position = str(row['position']) if pd.notnull(row['position']) and row['position'] != '' else ''
                                        
                                        # Determine if this is a substitute
                                        is_sub = pd.notnull(row.get('sub')) and bool(row.get('sub'))
                                        
                                        # Get batting order
                                        order_num = row.get('order')
                                        has_order = pd.notnull(order_num) and order_num is not None
                                        
                                        # Build the display string
                                        prefix = "    " if is_sub else ""  # Four spaces for indentation
                                        order_str = f"{int(order_num)}. " if not is_sub and has_order else ""
                                        pos_str = f" ({position})" if position else ""
                                        
                                        return f"{prefix}{order_str}{name}{pos_str}"
                                    except Exception as e:
                                        st.write(f"Debug - Error formatting player: {e}")
                                        st.write("Debug - Row data:", row.to_dict())
                                        return f"{row.get('name', 'Unknown')}"
                                
                                # Ensure required columns exist
                                if 'order' not in away_batting.columns:
                                    away_batting['order'] = None
                                if 'sub' not in away_batting.columns:
                                    away_batting['sub'] = False
                                if 'position' not in away_batting.columns:
                                    away_batting['position'] = ''
                                
                                # Convert order to numeric, keeping NaN values
                                away_batting['order'] = pd.to_numeric(away_batting['order'], errors='coerce')
                                
                                # Sort by batting order first
                                away_batting = away_batting.sort_values(
                                    by=['order'],
                                    na_position='last'
                                )
                                
                                # Create ordered display DataFrame
                                rows = []
                                sub_groups = {}  # Dictionary to hold substitutes for each batting order
                                other_subs = []  # For substitutes without a batting order
                                
                                # First pass: identify starters and build a map of who replaced whom
                                player_subs = {}  # Dictionary to map players to their substitutes
                                starter_by_position = {}  # Keep track of starters by position
                                
                                for _, row in away_batting.iterrows():
                                    if not row['sub']:
                                        # It's a starter
                                        rows.append(row)
                                        if pd.notnull(row['position']) and row['position']:
                                            starter_by_position[row['position']] = row['name']
                                    else:
                                        # It's a substitute, find who they replaced
                                        if pd.notnull(row['position']) and row['position'] in starter_by_position:
                                            # Find the starter they replaced
                                            starter_name = starter_by_position[row['position']]
                                            if starter_name not in player_subs:
                                                player_subs[starter_name] = []
                                            player_subs[starter_name].append(row)
                                        else:
                                            other_subs.append(row)
                                
                                # Second pass: create the final order with subs right after their starters
                                final_rows = []
                                for row in rows:
                                    final_rows.append(row)
                                    # Add any substitutes for this player right after them
                                    if row['name'] in player_subs:
                                        final_rows.extend(player_subs[row['name']])
                                
                                # Add any unmatched substitutes at the end
                                final_rows.extend(other_subs)
                                
                                # Create new DataFrame with correct order
                                away_batting = pd.DataFrame(final_rows)
                                
                                away_batting['Player'] = away_batting.apply(format_player_name, axis=1)
                                
                                # Reorder columns for better presentation
                                columns_order = ['Player', 'at_bats', 'hits', 'runs', 'rbis', 
                                               'doubles', 'triples', 'home_runs', 'walks', 
                                               'strikeouts', 'stolen_bases', 'caught_stealing']
                                
                                # Create final DataFrame for display
                                display_columns = ['Player'] + [col for col in columns_order if col in away_batting.columns and col != 'Player']
                                away_batting_display = away_batting[display_columns].copy()
                                
                                # Rename columns for better presentation
                                column_names = {
                                    'at_bats': 'AB',
                                    'hits': 'H',
                                    'runs': 'R',
                                    'rbis': 'RBI',
                                    'doubles': '2B',
                                    'triples': '3B',
                                    'home_runs': 'HR',
                                    'walks': 'BB',
                                    'strikeouts': 'SO',
                                    'stolen_bases': 'SB',
                                    'caught_stealing': 'CS'
                                }
                                away_batting_display.rename(columns=column_names, inplace=True)
                                
                                st.dataframe(away_batting_display, 
                                           use_container_width=True,
                                           hide_index=True)
                                
                                # Calculate and display game totals and notes
                                doubles = away_batting['doubles'].sum() if 'doubles' in away_batting.columns else 0
                                triples = away_batting['triples'].sum() if 'triples' in away_batting.columns else 0
                                homers = away_batting['home_runs'].sum() if 'home_runs' in away_batting.columns else 0
                                stolen = away_batting['stolen_bases'].sum() if 'stolen_bases' in away_batting.columns else 0
                                caught = away_batting['caught_stealing'].sum() if 'caught_stealing' in away_batting.columns else 0
                                gidp = away_batting['gidp'].sum() if 'gidp' in away_batting.columns else 0
                                errors = away_batting['errors'].sum() if 'errors' in away_batting.columns else 0
                                lob = away_batting['lob'].sum() if 'lob' in away_batting.columns else 0
                                
                                # Calculate total bases
                                singles = away_batting['hits'].sum() - (doubles + triples + homers) if 'hits' in away_batting.columns else 0
                                total_bases = singles + (2 * doubles) + (3 * triples) + (4 * homers)
                                
                                # Display game notes in MLB standard format
                                notes = []
                                if doubles > 0:
                                    notes.append(f"2B ({doubles}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('doubles', 0) > 0])}")
                                if triples > 0:
                                    notes.append(f"3B ({triples}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('triples', 0) > 0])}")
                                if homers > 0:
                                    notes.append(f"HR ({homers}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('home_runs', 0) > 0])}")
                                if stolen > 0:
                                    notes.append(f"SB ({stolen}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('stolen_bases', 0) > 0])}")
                                if caught > 0:
                                    notes.append(f"CS ({caught}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('caught_stealing', 0) > 0])}")
                                if gidp > 0:
                                    notes.append(f"GIDP ({gidp}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('gidp', 0) > 0])}")
                                if errors > 0:
                                    notes.append(f"E ({errors}): {', '.join([row['name'] for _, row in away_batting.iterrows() if row.get('errors', 0) > 0])}")
                                
                                st.markdown("---")
                                st.markdown("**Game Notes:**")
                                if notes:
                                    st.markdown(" • " + "\n • ".join(notes))
                                st.markdown(f"**TB:** {total_bases} • **LOB:** {lob}")
                            else:
                                st.info("No away team batting data available")
                            
                            # Display home team batting
                            st.markdown("#### Home Team Batting")
                            home_batting_data = game.get('home_team_batting', [])
                            if home_batting_data:
                                # Create DataFrame and sort by batting order
                                home_batting = pd.DataFrame(home_batting_data)
                                
                                # Ensure required columns exist before processing
                                required_columns = ['name', 'order', 'sub', 'position']
                                for col in required_columns:
                                    if col not in home_batting.columns:
                                        home_batting[col] = None
                                
                                # Add order column if not present
                                home_batting['order'] = pd.to_numeric(home_batting['order'], errors='coerce')
                                home_batting['sub'] = home_batting['sub'].fillna(False)
                                
                                # Sort by batting order first
                                home_batting = home_batting.sort_values(
                                    by=['order'],
                                    na_position='last'
                                )
                                
                                # Create ordered display DataFrame
                                rows = []
                                sub_groups = {}  # Dictionary to hold substitutes for each batting order
                                other_subs = []  # For substitutes without a batting order
                                
                                # First pass: identify starters and build a map of who replaced whom
                                player_subs = {}  # Dictionary to map players to their substitutes
                                starter_by_position = {}  # Keep track of starters by position
                                
                                for _, row in home_batting.iterrows():
                                    if not row['sub']:
                                        # It's a starter
                                        rows.append(row)
                                        if pd.notnull(row['position']) and row['position']:
                                            starter_by_position[row['position']] = row['name']
                                    else:
                                        # It's a substitute, find who they replaced
                                        if pd.notnull(row['position']) and row['position'] in starter_by_position:
                                            # Find the starter they replaced
                                            starter_name = starter_by_position[row['position']]
                                            if starter_name not in player_subs:
                                                player_subs[starter_name] = []
                                            player_subs[starter_name].append(row)
                                        else:
                                            other_subs.append(row)
                                
                                # Second pass: create the final order with subs right after their starters
                                final_rows = []
                                for row in rows:
                                    final_rows.append(row)
                                    # Add any substitutes for this player right after them
                                    if row['name'] in player_subs:
                                        final_rows.extend(player_subs[row['name']])
                                
                                # Add any unmatched substitutes at the end
                                final_rows.extend(other_subs)
                                
                                # Create new DataFrame with correct order
                                home_batting = pd.DataFrame(final_rows)
                                
                                # Format player names with indentation for substitutes
                                def format_player_name(row):
                                    try:
                                        prefix = "    " if row.get('sub', False) else ""
                                        order = f"{int(row['order'])}. " if 'order' in row and pd.notnull(row['order']) else "   "
                                        pos = f" ({row['position']})" if 'position' in row and row['position'] else ""
                                        return f"{prefix}{order}{row['name']}{pos}"
                                    except:
                                        return f"{row.get('name', 'Unknown')}"
                                
                                home_batting['Player'] = home_batting.apply(format_player_name, axis=1)
                                
                                # Create final DataFrame for display
                                display_columns = ['Player'] + [col for col in columns_order if col in home_batting.columns and col != 'Player']
                                home_batting_display = home_batting[display_columns].copy()
                                
                                # Use same column names as away team
                                home_batting_display.rename(columns=column_names, inplace=True)
                                
                                st.dataframe(home_batting_display, 
                                           use_container_width=True,
                                           hide_index=True)
                                
                                # Calculate and display game totals and notes
                                doubles = home_batting['doubles'].sum() if 'doubles' in home_batting.columns else 0
                                triples = home_batting['triples'].sum() if 'triples' in home_batting.columns else 0
                                homers = home_batting['home_runs'].sum() if 'home_runs' in home_batting.columns else 0
                                stolen = home_batting['stolen_bases'].sum() if 'stolen_bases' in home_batting.columns else 0
                                caught = home_batting['caught_stealing'].sum() if 'caught_stealing' in home_batting.columns else 0
                                gidp = home_batting['gidp'].sum() if 'gidp' in home_batting.columns else 0
                                errors = home_batting['errors'].sum() if 'errors' in home_batting.columns else 0
                                lob = home_batting['lob'].sum() if 'lob' in home_batting.columns else 0
                                
                                # Calculate total bases
                                singles = home_batting['hits'].sum() - (doubles + triples + homers) if 'hits' in home_batting.columns else 0
                                total_bases = singles + (2 * doubles) + (3 * triples) + (4 * homers)
                                
                                # Display game notes in MLB standard format
                                notes = []
                                if doubles > 0:
                                    notes.append(f"2B ({doubles}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('doubles', 0) > 0])}")
                                if triples > 0:
                                    notes.append(f"3B ({triples}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('triples', 0) > 0])}")
                                if homers > 0:
                                    notes.append(f"HR ({homers}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('home_runs', 0) > 0])}")
                                if stolen > 0:
                                    notes.append(f"SB ({stolen}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('stolen_bases', 0) > 0])}")
                                if caught > 0:
                                    notes.append(f"CS ({caught}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('caught_stealing', 0) > 0])}")
                                if gidp > 0:
                                    notes.append(f"GIDP ({gidp}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('gidp', 0) > 0])}")
                                if errors > 0:
                                    notes.append(f"E ({errors}): {', '.join([row['name'] for _, row in home_batting.iterrows() if row.get('errors', 0) > 0])}")
                                
                                st.markdown("---")
                                st.markdown("**Game Notes:**")
                                if notes:
                                    st.markdown(" • " + "\n • ".join(notes))
                                st.markdown(f"**TB:** {total_bases} • **LOB:** {lob}")
                            else:
                                st.info("No home team batting data available")
                        
                    with tabs[1]:  # Pitching Stats
                        # Display away team pitching
                        st.markdown("#### Away Team Pitching")
                        away_pitching = None
                        
                        # Get away team pitching stats
                        away_pitching_data = game.get('away_team_pitching', [])
                        if away_pitching_data:
                            away_pitching = pd.DataFrame(away_pitching_data)
                            # Reorder columns for better presentation
                            columns_order = ['name', 'innings_pitched', 'hits_allowed', 'runs_allowed', 
                                           'earned_runs', 'walks', 'strikeouts', 'home_runs_allowed']
                            away_pitching = away_pitching.reindex(columns=[col for col in columns_order if col in away_pitching.columns])
                            st.dataframe(away_pitching, use_container_width=True)
                        else:
                            st.info("No away team pitching data available")
                        
                        # Display home team pitching
                        st.markdown("#### Home Team Pitching")
                        home_pitching = None                        # Get home team pitching stats
                        home_pitching_data = game.get('home_team_pitching', [])
                        if home_pitching_data:
                            home_pitching = pd.DataFrame(home_pitching_data)
                            # Reorder columns for better presentation
                            home_pitching = home_pitching.reindex(columns=[col for col in columns_order if col in home_pitching.columns])
                            st.dataframe(home_pitching, use_container_width=True)
                        else:
                            st.info("No home team pitching data available")
                    
                    with tabs[2]:  # Game Info
                        # Display general game information
                        st.markdown("#### Game Details")
                        game_info = {
                            "Date": game.get('date'),
                            "Venue": game.get('venue'),
                            "Status": game.get('game_status'),
                            "Final Score": f"{game.get('away_team')} {game.get('away_score')} @ {game.get('home_team')} {game.get('home_score')}"
                        }
                        if game.get('notes'):
                            game_info["Notes"] = game.get('notes')
                        
                        if game_info:
                            if isinstance(game_info, dict):
                                for key, value in game_info.items():
                                    key_display = key.replace('_', ' ').title()
                                    st.markdown(f"**{key_display}:** {value}")
                            elif isinstance(game_info, list):
                                st.dataframe(pd.DataFrame(game_info), use_container_width=True)
                            else:
                                st.write(game_info)
                        else:
                            st.info("No additional game information available")
                else:
                    st.info("No box score available for this game.")

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
            max_games = int(batting_df['games'].max()) if 'games' in batting_df.columns and len(batting_df) > 0 else 1
            if max_games > 1:
                min_games = st.slider("Minimum games played", 1, max_games, 1)
            else:
                min_games = 1
                st.info("All players have played 1 game or less. Showing all available data.")
            filtered_batting = batting_df[batting_df['games'] >= min_games] if 'games' in batting_df.columns else batting_df
            
            # Rename columns to standard baseball abbreviations
            batting_display = filtered_batting.copy()
            
            # Format decimal statistics to baseball standard (.xxx format)
            decimal_columns = ['batting_average', 'on_base_percentage', 'slugging_percentage', 'ops']
            for col in decimal_columns:
                if col in batting_display.columns:
                    batting_display[col] = batting_display[col].apply(
                        lambda x: f"{x:.3f}".lstrip('0') if pd.notnull(x) and x < 1 else f"{x:.3f}" if pd.notnull(x) else ""
                    )
            
            batting_column_names = {
                'games': 'G',
                'at_bats': 'AB',
                'hits': 'H',
                'runs': 'R',
                'rbis': 'RBI',
                'doubles': '2B',
                'triples': '3B',
                'home_runs': 'HR',
                'walks': 'BB',
                'strikeouts': 'SO',
                'stolen_bases': 'SB',
                'caught_stealing': 'CS',
                'batting_average': 'AVG',
                'on_base_percentage': 'OBP',
                'slugging_percentage': 'SLG',
                'ops': 'OPS'
            }
            batting_display.rename(columns=batting_column_names, inplace=True)
            
            st.dataframe(batting_display, use_container_width=True)
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
            max_games = int(pitching_df['games'].max()) if 'games' in pitching_df.columns and len(pitching_df) > 0 else 1
            if max_games > 1:
                min_games = st.slider("Minimum games pitched", 1, max_games, 1, key="pitching_filter")
            else:
                min_games = 1
                st.info("All pitchers have pitched 1 game or less. Showing all available data.")
            filtered_pitching = pitching_df[pitching_df['games'] >= min_games] if 'games' in pitching_df.columns else pitching_df
            
            # Rename columns to standard baseball abbreviations
            pitching_display = filtered_pitching.copy()
            
            # Format decimal statistics to baseball standard (.xxx format)
            pitching_decimal_columns = ['earned_run_average', 'whip']
            for col in pitching_decimal_columns:
                if col in pitching_display.columns:
                    if col == 'earned_run_average':
                        # ERA typically shows 2 decimal places but in x.xx format (keep leading zero)
                        pitching_display[col] = pitching_display[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
                    else:  # WHIP
                        # WHIP typically shows 3 decimal places, remove leading zero if < 1
                        pitching_display[col] = pitching_display[col].apply(
                            lambda x: f"{x:.3f}".lstrip('0') if pd.notnull(x) and x < 1 else f"{x:.3f}" if pd.notnull(x) else ""
                        )
            
            pitching_column_names = {
                'games': 'G',
                'innings_pitched': 'IP',
                'hits_allowed': 'H',
                'runs_allowed': 'R',
                'earned_runs': 'ER',
                'walks': 'BB',
                'strikeouts': 'SO',
                'home_runs_allowed': 'HR',
                'earned_run_average': 'ERA',
                'whip': 'WHIP',
                'wins': 'W',
                'losses': 'L',
                'saves': 'SV',
                'holds': 'HLD'
            }
            pitching_display.rename(columns=pitching_column_names, inplace=True)
            
            st.dataframe(pitching_display, use_container_width=True)
        else:
            st.info("No pitching statistics available.")

def dashboard_page():
    st.header("📊 Baseball Statistics Dashboard")
    
    games = st.session_state.data_manager.get_all_games()
    
    if not games:
        st.info("🎯 No games added yet. Add some games to see visualizations and insights!")
        return
    
    # Calculate stats for visualization
    batting_stats, pitching_stats = st.session_state.stats_calculator.calculate_aggregate_stats(games)
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Games Attended", len(games))
    
    with col2:
        total_players = len(batting_stats) if batting_stats else 0
        st.metric("⚾ Players Watched", total_players)
    
    with col3:
        total_runs = sum(int(g.get('home_score', 0)) + int(g.get('away_score', 0)) for g in games)
        avg_runs = total_runs / len(games) if games else 0
        st.metric("🏃‍♂️ Avg Runs per Game", f"{avg_runs:.1f}")
    
    with col4:
        dates = [g.get('date') for g in games if g.get('date')]
        if dates:
            latest_date = max(dates)
            st.metric("📅 Latest Game", latest_date)
    
    st.markdown("---")
    
    # Interactive filters
    st.subheader("🎛️ Filter Your Data")
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Team filter
        all_teams = set()
        for g in games:
            if g.get('home_team'):
                all_teams.add(g.get('home_team'))
            if g.get('away_team'):
                all_teams.add(g.get('away_team'))
        
        selected_teams = st.multiselect(
            "Filter by Teams:",
            sorted(all_teams),
            default=[],
            help="Leave empty to show all teams"
        )
    
    with col_filter2:
        # Date range filter
        game_dates = [datetime.strptime(g.get('date'), '%Y-%m-%d').date() for g in games if g.get('date')]
        if game_dates:
            min_date, max_date = min(game_dates), max(game_dates)
            date_range = st.date_input(
                "Date Range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter games by date range"
            )
        else:
            date_range = None
    
    # Apply filters
    filtered_games = games
    if selected_teams:
        filtered_games = [g for g in filtered_games 
                         if g.get('home_team') in selected_teams or g.get('away_team') in selected_teams]
    
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_games = [g for g in filtered_games 
                         if start_date <= datetime.strptime(g.get('date'), '%Y-%m-%d').date() <= end_date]
    
    st.markdown("---")
    
    # Visualizations with filtered data
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏟️ Teams", "📊 Performance", "🎯 Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Games by month chart
            st.subheader("📅 Games by Month")
            games_by_month = {}
            for g in filtered_games:
                d = g.get('date', 'Unknown')
                try:
                    dt = datetime.strptime(d, '%Y-%m-%d')
                    month_str = dt.strftime('%Y-%m')
                except Exception:
                    month_str = 'Unknown'
                games_by_month[month_str] = games_by_month.get(month_str, 0) + 1
            
            if games_by_month:
                months_df = pd.DataFrame([
                    {"Month": k, "Games": v} 
                    for k, v in sorted(games_by_month.items())
                ])
                fig_months = px.bar(months_df, x='Month', y='Games', 
                                   title="Games Attended Over Time",
                                   color='Games', 
                                   color_continuous_scale='blues')
                fig_months.update_layout(height=400)
                st.plotly_chart(fig_months, use_container_width=True)
        
        with col2:
            # Score distribution
            st.subheader("⚾ Score Distribution")
            home_scores = [int(g.get('home_score', 0)) for g in filtered_games]
            away_scores = [int(g.get('away_score', 0)) for g in filtered_games]
            
            scores_df = pd.DataFrame({
                'Score': home_scores + away_scores,
                'Type': ['Home'] * len(home_scores) + ['Away'] * len(away_scores)
            })
            
            fig_scores = px.histogram(scores_df, x='Score', color='Type', 
                                     title="Score Distribution",
                                     barmode='overlay',
                                     opacity=0.7)
            fig_scores.update_layout(height=400)
            st.plotly_chart(fig_scores, use_container_width=True)
    
    with tab2:
        # Team analysis
        st.subheader("🏟️ Team Performance Analysis")
        
        # Team records calculation
        records = {}
        for g in filtered_games:
            home = g.get('home_team')
            away = g.get('away_team')
            hs = g.get('home_score')
            ascore = g.get('away_score')
            
            if home is None or away is None or hs is None or ascore is None:
                continue
                
            for t in (home, away):
                if t not in records:
                    records[t] = {"Games":0, "Wins":0, "Losses":0, "Ties":0, 
                                "Runs_For":0, "Runs_Against":0}
            
            records[home]["Games"] += 1
            records[away]["Games"] += 1
            records[home]["Runs_For"] += int(hs)
            records[home]["Runs_Against"] += int(ascore)
            records[away]["Runs_For"] += int(ascore)
            records[away]["Runs_Against"] += int(hs)
            
            if int(hs) > int(ascore):
                records[home]["Wins"] += 1
                records[away]["Losses"] += 1
            elif int(hs) < int(ascore):
                records[away]["Wins"] += 1
                records[home]["Losses"] += 1
            else:
                records[home]["Ties"] += 1
                records[away]["Ties"] += 1
        
        if records:
            records_list = []
            for team, stats in records.items():
                win_pct = (stats["Wins"] / stats["Games"]) if stats["Games"] > 0 else 0
                records_list.append({
                    "Team": team,
                    "Games": stats["Games"],
                    "Wins": stats["Wins"],
                    "Losses": stats["Losses"],
                    "Win%": win_pct,
                    "Runs_For": stats["Runs_For"],
                    "Runs_Against": stats["Runs_Against"],
                    "Run_Diff": stats["Runs_For"] - stats["Runs_Against"]
                })
            
            records_df = pd.DataFrame(records_list)
            records_df = records_df.sort_values('Win%', ascending=False)
            
            # Top performers chart
            top_teams = records_df.head(10)
            fig_teams = px.bar(top_teams, x='Team', y='Win%', 
                              title="Top 10 Teams by Win Percentage",
                              color='Win%', 
                              color_continuous_scale='RdYlGn')
            fig_teams.update_xaxes(tickangle=45)
            fig_teams.update_layout(height=500)
            st.plotly_chart(fig_teams, use_container_width=True)
            
            # Detailed table
            st.subheader("📋 Complete Team Records")
            records_df['Win%'] = records_df['Win%'].apply(lambda x: f"{x:.3f}")
            st.dataframe(records_df, use_container_width=True, hide_index=True)
    
    with tab3:
        # Performance metrics
        st.subheader("🎯 Performance Insights")
        
        if batting_stats and len(batting_stats) > 0:
            batting_df = pd.DataFrame(batting_stats)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top batting averages
                if 'batting_average' in batting_df.columns and 'games' in batting_df.columns:
                    qualified_batters = batting_df[batting_df['games'] >= 3]
                    if len(qualified_batters) > 0:
                        top_avg = qualified_batters.nlargest(10, 'batting_average')
                        fig_avg = px.bar(top_avg.head(8), 
                                       x='batting_average', y='player_name',
                                       orientation='h',
                                       title='Top Batting Averages (Min 3 Games)',
                                       color='batting_average',
                                       color_continuous_scale='viridis')
                        fig_avg.update_layout(height=400)
                        st.plotly_chart(fig_avg, use_container_width=True)
                    else:
                        st.info("Need players with 3+ games for batting average leaderboard")
            
            with col2:
                # Home runs leaders
                if 'home_runs' in batting_df.columns:
                    hr_leaders = batting_df[batting_df['home_runs'] > 0].nlargest(10, 'home_runs')
                    if len(hr_leaders) > 0:
                        fig_hr = px.bar(hr_leaders.head(8), 
                                      x='home_runs', y='player_name',
                                      orientation='h',
                                      title='Home Run Leaders',
                                      color='home_runs',
                                      color_continuous_scale='Reds')
                        fig_hr.update_layout(height=400)
                        st.plotly_chart(fig_hr, use_container_width=True)
                    else:
                        st.info("No home runs recorded yet!")
        else:
            st.info("No player statistics available yet. Add some games to see player performance!")
    
    with tab4:
        # Advanced insights
        st.subheader("🎯 Advanced Insights")
        
        # Game outcome analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Game Outcomes")
            outcomes = {'Home Wins': 0, 'Away Wins': 0, 'Ties': 0}
            
            for g in filtered_games:
                hs = int(g.get('home_score', 0))
                ascore = int(g.get('away_score', 0))
                
                if hs > ascore:
                    outcomes['Home Wins'] += 1
                elif ascore > hs:
                    outcomes['Away Wins'] += 1
                else:
                    outcomes['Ties'] += 1
            
            outcomes_df = pd.DataFrame([
                {"Outcome": k, "Count": v} for k, v in outcomes.items()
            ])
            
            fig_outcomes = px.pie(outcomes_df, values='Count', names='Outcome',
                                title="Home vs Away Win Distribution",
                                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1'])
            st.plotly_chart(fig_outcomes, use_container_width=True)
        
        with col2:
            # Scoring trends
            st.subheader("📈 Scoring Trends")
            if filtered_games:
                game_dates = []
                total_runs = []
                
                for g in sorted(filtered_games, key=lambda x: x.get('date', '')):
                    try:
                        date = datetime.strptime(g.get('date'), '%Y-%m-%d')
                        runs = int(g.get('home_score', 0)) + int(g.get('away_score', 0))
                        game_dates.append(date)
                        total_runs.append(runs)
                    except:
                        continue
                
                if game_dates:
                    trends_df = pd.DataFrame({
                        'Date': game_dates,
                        'Total_Runs': total_runs
                    })
                    
                    fig_trends = px.line(trends_df, x='Date', y='Total_Runs',
                                       title="Total Runs per Game Over Time",
                                       markers=True)
                    fig_trends.add_hline(y=sum(total_runs)/len(total_runs), 
                                       line_dash="dash", 
                                       annotation_text=f"Average: {sum(total_runs)/len(total_runs):.1f}")
                    st.plotly_chart(fig_trends, use_container_width=True)
        
        # Summary insights
        st.markdown("### 💡 Key Insights")
        
        insights = []
        if filtered_games:
            avg_score = sum(int(g.get('home_score', 0)) + int(g.get('away_score', 0)) 
                           for g in filtered_games) / len(filtered_games)
            insights.append(f"📊 Average total runs per game: **{avg_score:.1f}**")
            
            home_win_pct = outcomes.get('Home Wins', 0) / len(filtered_games) * 100
            insights.append(f"🏠 Home team wins **{home_win_pct:.1f}%** of games you've attended")
            
            if batting_stats:
                total_players = len(batting_stats)
                insights.append(f"👥 You've watched **{total_players}** different players across all games")
            
            most_common_teams = {}
            for g in filtered_games:
                for team in [g.get('home_team'), g.get('away_team')]:
                    if team:
                        most_common_teams[team] = most_common_teams.get(team, 0) + 1
            
            if most_common_teams:
                fav_team = max(most_common_teams.items(), key=lambda x: x[1])
                insights.append(f"⭐ Most watched team: **{fav_team[0]}** ({fav_team[1]} games)")
        
        for insight in insights:
            st.markdown(f"- {insight}")
        
        if not insights:
            st.info("Add more games to see personalized insights!")

def export_data_page():
    st.header("Export Player Statistics")

    games = st.session_state.data_manager.get_all_games()

    if not games:
        st.info("No data to export. Add some games first.")
        return

    st.write("Export aggregated player statistics from all your attended games.")

    # Calculate aggregated stats
    batting_stats, pitching_stats = st.session_state.stats_calculator.calculate_aggregate_stats(games)

    export_format = st.selectbox(
        "Select export format",
        ["JSON", "CSV"]
    )

    if st.button("Generate Export", type="primary"):
        try:
            if export_format == "JSON":
                # Export aggregated player stats as JSON
                export_data = {
                    "batting_stats": batting_stats,
                    "pitching_stats": pitching_stats,
                    "export_date": datetime.now().isoformat(),
                    "total_games": len(games),
                    "total_batters": len(batting_stats),
                    "total_pitchers": len(pitching_stats)
                }

                json_str = json.dumps(export_data, indent=2, default=str)

                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"player_stats_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )

            elif export_format == "CSV":
                # Export batting stats as CSV
                if batting_stats:
                    batting_df = pd.DataFrame(batting_stats)
                    batting_csv = batting_df.to_csv(index=False)

                    st.download_button(
                        label="Download Batting Stats CSV",
                        data=batting_csv,
                        file_name=f"batting_stats_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="batting_csv"
                    )

                # Export pitching stats as CSV
                if pitching_stats:
                    pitching_df = pd.DataFrame(pitching_stats)
                    pitching_csv = pitching_df.to_csv(index=False)

                    st.download_button(
                        label="Download Pitching Stats CSV",
                        data=pitching_csv,
                        file_name=f"pitching_stats_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="pitching_csv"
                    )

        except Exception as e:
            st.error(f"Error generating export: {str(e)}")

    # Display summary statistics
    st.subheader("Export Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Games", len(games))

    with col2:
        st.metric("Total Batters", len(batting_stats))

    with col3:
        st.metric("Total Pitchers", len(pitching_stats))

if __name__ == "__main__":
    main()
