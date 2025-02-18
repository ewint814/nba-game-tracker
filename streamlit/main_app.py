import streamlit as st
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json
import time
import gc
from nba_api.stats.endpoints import boxscoreadvancedv3

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from src.data.basketball_reference_scraper import BasketballReferenceScraper
from src.data.database_models import Game, Photo, Base, InactivePlayer, Official, QuarterScores, TeamStats, SeriesStats, LastMeeting, VenueInfo, GameFlow, PlayerAdvancedStats, TeamAdvancedStats
from src.data.nba_api_client import NBAApiClient
from src.utils.game_calculations import format_season, calculate_series_stats

# Initialize database connection
engine = create_engine('sqlite:///basketball_tracker.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def recreate_database():
    """
    Recreate the database with the latest schema.
    TODO: Remove this function before moving to production.
    Only for development use to handle schema changes.
    """
    try:
        # Close all sessions and connections
        Session.close_all()
        engine.dispose()
        
        # Sleep briefly to ensure connections are closed
        time.sleep(1)
        
        # Force Python garbage collection
        gc.collect()
        
        # Remove existing database
        if os.path.exists('basketball_tracker.db'):
            try:
                os.remove('basketball_tracker.db')
                st.success("Existing database removed")
            except PermissionError:
                st.error("Could not remove database - please close any other applications using it")
                return
            except Exception as e:
                st.error(f"Error removing database: {str(e)}")
                return
        
        # Create new database with current schema
        new_engine = create_engine('sqlite:///basketball_tracker.db')
        Base.metadata.create_all(new_engine)
        st.success("New database created with updated schema")
        
        # Refresh the page to ensure clean state
        st.rerun()
        
    except Exception as e:
        st.error(f"Error recreating database: {str(e)}")

def main():
    """Main function that sets up the Streamlit app structure."""
    st.title("Basketball Game Tracker")
    
    # TODO: Remove this section before production
    # Development tools
    if st.sidebar.checkbox("Show Dev Tools"):
        if st.sidebar.button("Recreate Database"):
            recreate_database()
    
    # Create sidebar navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Add Game", "My Games", "Statistics", "Test API", "Database Preview"]
    )
    
    if page == "Add Game":
        show_add_game()
    elif page == "My Games":
        show_my_games()
    elif page == "Statistics":
        show_statistics()
    elif page == "Test API":
        show_test_data()
    elif page == "Database Preview":
        show_database_preview()

def show_add_game():
    """Form to add a new game you've attended."""
    st.header("Add Game")
    
    # Step 1: Find the game
    st.subheader("Step 1: Find the Game")
    date = st.date_input(
        "Game Date",
        value=datetime.now() - timedelta(days=1)
    )
    
    # Store games in session state
    if 'available_games' not in st.session_state:
        st.session_state.available_games = []
        
    if st.button("Find Games"):
        client = NBAApiClient()
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            games = client.get_games_for_date(date_str)
            st.session_state.available_games = games
            
            if not games:
                st.info("No games found for this date")
            else:
                st.success(f"Found {len(games)} games!")
            
        except Exception as e:
            st.error(f"Error fetching games: {str(e)}")
    
    # Show game selection if games are available
    if st.session_state.available_games:
        game_options = [
            f"{game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']}) - {game['arena']}"
            for game in st.session_state.available_games
        ]
        selected_game = st.radio("Select Game:", game_options)
        
        # Step 2: Add attendance details
        if selected_game:
            st.subheader("Step 2: Add Your Details")
            
            # Game attendance details form
            with st.form("attendance_details"):
                seat_section = st.text_input("Seat Section (e.g., Loge 12)")
                seat_row = st.text_input("Row")
                seat_number = st.text_input("Seat Number")
                attended_with = st.text_input("Attended With")
                notes = st.text_area("Notes")
                
                if st.form_submit_button("Save Game"):
                    client = NBAApiClient()
                    
                    # Get the selected game data
                    game_idx = game_options.index(selected_game)
                    game_data = st.session_state.available_games[game_idx].copy()
                    
                    try:
                        # Get detailed stats when saving
                        with st.spinner("Getting detailed game stats..."):
                            detailed_stats = client.get_detailed_stats(game_data['game_id'])
                        
                        # Calculate pre-game series data
                        series_data = calculate_series_stats(
                            home_score=game_data['home_score'],
                            away_score=game_data['away_score'],
                            postgame_home_wins=detailed_stats['home_team_series_wins'],
                            postgame_home_losses=detailed_stats['home_team_series_losses'],
                            postgame_leader=detailed_stats['series_leader'],
                            home_team_abbrev=detailed_stats['home_team_abbrev'],
                            away_team_abbrev=detailed_stats['away_team_abbrev']
                        )
                        
                        # Create new game without series stats and last meeting fields
                        session = Session()
                        try:
                            # Create new game without the team stats fields
                            new_game = Game(
                                date=date,
                                home_team=game_data['home_team'],
                                away_team=game_data['away_team'],
                                home_score=game_data['home_score'],
                                away_score=game_data['away_score'],
                                seat_section=seat_section,
                                seat_row=seat_row,
                                seat_number=seat_number,
                                attended_with=attended_with,
                                notes=notes,
                                game_id=game_data['game_id'],
                                season=format_season(detailed_stats['season'][:4]),
                                home_team_id=detailed_stats['home_team_id'],
                                away_team_id=detailed_stats['visitor_team_id'],
                                home_team_abbrev=detailed_stats['home_team_abbrev'],
                                away_team_abbrev=detailed_stats['away_team_abbrev']
                            )

                            # Create series stats
                            series_stats = SeriesStats(
                                game_id=str(game_data['game_id']),
                                # Pre-game series data
                                pregame_home_team_series_wins=series_data['pregame_home_wins'],
                                pregame_home_team_series_losses=series_data['pregame_home_losses'],
                                pregame_series_leader=series_data['pregame_leader'],
                                pregame_series_record=series_data['pregame_series_record'],
                                # Post-game series data
                                postgame_home_team_series_wins=detailed_stats['home_team_series_wins'],
                                postgame_home_team_series_losses=detailed_stats['home_team_series_losses'],
                                postgame_series_leader=detailed_stats['series_leader'],
                                postgame_series_record=f"{detailed_stats['home_team_series_wins']}-{detailed_stats['home_team_series_losses']}"
                            )
                            session.add(series_stats)
                            
                            # Create last meeting record
                            last_meeting = LastMeeting(
                                game_id=str(game_data['game_id']),
                                last_meeting_game_id=detailed_stats['last_meeting_game_id'],
                                last_meeting_game_date=datetime.strptime(detailed_stats['last_meeting_game_date'], '%Y-%m-%dT%H:%M:%S').date(),
                                home_team_id=detailed_stats['last_meeting_home_team_id'],
                                away_team_id=detailed_stats['last_meeting_visitor_team_id'],
                                home_team_score=detailed_stats['last_meeting_home_points'],
                                away_team_score=detailed_stats['last_meeting_visitor_points']
                            )
                            session.add(last_meeting)
                            
                            # Create home team stats without largest lead
                            home_stats = TeamStats(
                                game_id=str(game_data['game_id']),
                                team_id=detailed_stats['home_team_id'],
                                paint_points=detailed_stats['home_paint_points'],
                                second_chance_points=detailed_stats['home_second_chance_points'],
                                fast_break_points=detailed_stats['home_fast_break_points'],
                                team_turnovers=detailed_stats['home_team_turnovers'],
                                total_turnovers=detailed_stats['home_total_turnovers'],
                                team_rebounds=detailed_stats['home_team_rebounds'],
                                points_off_to=detailed_stats['home_points_off_to']
                            )
                            session.add(home_stats)
                            
                            # Create away team stats without largest lead
                            away_stats = TeamStats(
                                game_id=str(game_data['game_id']),
                                team_id=detailed_stats['visitor_team_id'],
                                paint_points=detailed_stats['away_paint_points'],
                                second_chance_points=detailed_stats['away_second_chance_points'],
                                fast_break_points=detailed_stats['away_fast_break_points'],
                                team_turnovers=detailed_stats['away_team_turnovers'],
                                total_turnovers=detailed_stats['away_total_turnovers'],
                                team_rebounds=detailed_stats['away_team_rebounds'],
                                points_off_to=detailed_stats['away_points_off_to']
                            )
                            session.add(away_stats)
                            
                            # Add quarter scores
                            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                            for quarter in quarters:
                                q_num = quarter[1]  # get the number
                                new_quarter = QuarterScores(
                                    game_id=str(game_data['game_id']),
                                    period=quarter,
                                    home_team_id=detailed_stats['home_team_id'],
                                    away_team_id=detailed_stats['visitor_team_id'],
                                    home_score=detailed_stats[f'home_q{q_num}'],
                                    away_score=detailed_stats[f'away_q{q_num}']
                                )
                                session.add(new_quarter)
                            
                            # Add overtime periods if they exist
                            ot = 1
                            while f'home_ot{ot}' in detailed_stats:
                                new_ot = QuarterScores(
                                    game_id=str(game_data['game_id']),
                                    period=f'OT{ot}',
                                    home_team_id=detailed_stats['home_team_id'],
                                    away_team_id=detailed_stats['visitor_team_id'],
                                    home_score=detailed_stats[f'home_ot{ot}'],
                                    away_score=detailed_stats[f'away_ot{ot}']
                                )
                                session.add(new_ot)
                                ot += 1

                            # Add inactive players
                            for player in detailed_stats['inactive_players']:
                                # Determine team_id based on team_abbrev
                                team_id = (detailed_stats['home_team_id'] 
                                           if player['team_abbrev'] == detailed_stats['home_team_abbrev']
                                           else detailed_stats['visitor_team_id'])
                                
                                inactive_player = InactivePlayer(
                                    game_id=str(game_data['game_id']),
                                    first_name=player['first_name'],
                                    last_name=player['last_name'],
                                    jersey_num=int(player['jersey_num'].strip()),
                                    team_id=team_id  # Use team_id instead of team_abbrev
                                )
                                session.add(inactive_player)

                            # Add officials separately
                            for official in detailed_stats['officials_complete']:
                                new_official = Official(
                                    game_id=str(game_data['game_id']),
                                    official_id=official['id'],
                                    name=f"{official['first_name']} {official['last_name']}",
                                    jersey_num=int(official['jersey_num'].strip())
                                )
                                session.add(new_official)

                            # Create venue info
                            venue_info = VenueInfo(
                                game_id=str(game_data['game_id']),
                                arena=game_data['arena'],
                                attendance=detailed_stats['attendance'],
                                duration_minutes=int(detailed_stats['duration'].split(':')[0]) * 60 + int(detailed_stats['duration'].split(':')[1]),  # Convert "H:MM" to minutes
                                national_tv=detailed_stats['national_tv'] if detailed_stats['national_tv'] else 'Local'
                            )
                            session.add(venue_info)

                            # Create game flow stats
                            game_flow = GameFlow(
                                game_id=str(game_data['game_id']),
                                lead_changes=detailed_stats['lead_changes'],
                                times_tied=detailed_stats['times_tied'],
                                home_largest_lead=detailed_stats['home_largest_lead'],
                                away_largest_lead=detailed_stats['away_largest_lead']
                            )
                            session.add(game_flow)

                            # Get advanced stats
                            advanced_data = client.get_advanced_stats(game_data['game_id'])
                            
                            # Create player advanced stats
                            for player in advanced_data['player_stats']:
                                stats = player.get('statistics', {})
                                
                                # Get position from COMMENT field and determine if player was a starter
                                position = player.get('comment', '').strip()
                                starter = bool(position and position in ['F', 'G', 'C'])
                                
                                player_advanced = PlayerAdvancedStats(
                                    game_id=str(game_data['game_id']),
                                    team_id=player['teamId'],
                                    player_id=player['personId'],
                                    first_name=player['firstName'],
                                    last_name=player['familyName'],
                                    position=position if starter else None,  # Only set position if they started
                                    starter=starter,
                                    minutes=stats.get('minutes'),
                                    pie=stats.get('pie'),
                                    estimated_offensive_rating=stats.get('estimatedOffensiveRating'),
                                    offensive_rating=stats.get('offensiveRating'),
                                    estimated_defensive_rating=stats.get('estimatedDefensiveRating'),
                                    defensive_rating=stats.get('defensiveRating'),
                                    estimated_net_rating=stats.get('estimatedNetRating'),
                                    net_rating=stats.get('netRating'),
                                    assist_percentage=stats.get('assistPercentage'),
                                    assist_to_turnover=stats.get('assistToTurnover'),
                                    assist_ratio=stats.get('assistRatio'),
                                    offensive_rebound_percentage=stats.get('offensiveReboundPercentage'),
                                    defensive_rebound_percentage=stats.get('defensiveReboundPercentage'),
                                    rebound_percentage=stats.get('reboundPercentage'),
                                    turnover_ratio=stats.get('turnoverRatio'),
                                    effective_field_goal_percentage=stats.get('effectiveFieldGoalPercentage'),
                                    true_shooting_percentage=stats.get('trueShootingPercentage'),
                                    usage_percentage=stats.get('usagePercentage'),
                                    estimated_usage_percentage=stats.get('estimatedUsagePercentage'),
                                    estimated_pace=stats.get('estimatedPace'),
                                    pace=stats.get('pace'),
                                    pace_per40=stats.get('pacePer40'),
                                    possessions=int(stats.get('possessions')) if stats.get('possessions') else None
                                )
                                session.add(player_advanced)
                            
                            # Create team advanced stats
                            for team in advanced_data['team_stats']:
                                stats = team.get('statistics', {})
                                
                                # Handle PIE case (uppercase in API)
                                if 'PIE' in stats:
                                    pie_value = stats['PIE']
                                else:
                                    pie_value = None
                                
                                team_advanced = TeamAdvancedStats(
                                    game_id=str(game_data['game_id']),
                                    team_id=team['teamId'],
                                    estimated_offensive_rating=stats.get('estimatedOffensiveRating'),
                                    offensive_rating=stats.get('offensiveRating'),
                                    estimated_defensive_rating=stats.get('estimatedDefensiveRating'),
                                    defensive_rating=stats.get('defensiveRating'),
                                    estimated_net_rating=stats.get('estimatedNetRating'),
                                    net_rating=stats.get('netRating'),
                                    assist_percentage=stats.get('assistPercentage'),
                                    assist_to_turnover=stats.get('assistToTurnover'),
                                    assist_ratio=stats.get('assistRatio'),
                                    offensive_rebound_percentage=stats.get('offensiveReboundPercentage'),
                                    defensive_rebound_percentage=stats.get('defensiveReboundPercentage'),
                                    rebound_percentage=stats.get('reboundPercentage'),
                                    estimated_team_turnover_percentage=stats.get('estimatedTeamTurnoverPercentage'),
                                    turnover_ratio=stats.get('turnoverRatio'),
                                    effective_field_goal_percentage=stats.get('effectiveFieldGoalPercentage'),
                                    true_shooting_percentage=stats.get('trueShootingPercentage'),
                                    estimated_pace=stats.get('estimatedPace'),
                                    pace=stats.get('pace'),
                                    pace_per40=stats.get('pacePer40'),
                                    possessions=int(stats.get('possessions')) if stats.get('possessions') else None,
                                    pie=pie_value
                                )
                                session.add(team_advanced)

                            session.add(new_game)
                            session.commit()
                            st.success("Game added successfully!")
                        except Exception as e:
                            st.error(f"Error saving game: {str(e)}")
                        finally:
                            session.close()
                    except Exception as e:
                        st.error(f"Error getting detailed stats: {str(e)}")

def show_my_games():
    """Display list of games you've attended."""
    st.header("My Games")
    
    session = Session()
    try:
        games = session.query(Game).order_by(Game.date.desc()).all()
        
        if games:
            for game in games:
                with st.expander(f"{game.date}: {game.home_team} vs {game.away_team}"):
                    st.write(f"Score: {game.home_score} - {game.away_score}")
                    st.write(f"Seat: Section {game.seat_section}, Row {game.seat_row}, Seat {game.seat_number}")
                    st.write(f"Attended with: {game.attended_with}")
                    if game.notes:
                        st.write(f"Notes: {game.notes}")
        else:
            st.info("No games added yet. Use the 'Add Game' page to start tracking your games!")
    finally:
        session.close()

def show_statistics():
    """Show Celtics-focused statistics dashboard about attended games."""
    st.header("Celtics Games Statistics Dashboard")
    
    session = Session()
    try:
        games = session.query(Game).all()
        
        if not games:
            st.info("Add some games to see statistics!")
            return

        # Overall Records Section
        st.subheader("Records")
        col1, col2, col3 = st.columns(3)
        
        # Calculate overall record
        total_games = len(games)
        celtics_wins = sum(1 for game in games if 
            (game.home_team == "Boston Celtics" and game.home_score > game.away_score) or
            (game.away_team == "Boston Celtics" and game.away_score > game.home_score))
        celtics_losses = total_games - celtics_wins
        
        # Home/Away records
        home_games = [g for g in games if g.home_team == "Boston Celtics"]
        away_games = [g for g in games if g.away_team == "Boston Celtics"]
        
        home_wins = sum(1 for g in home_games if g.home_score > g.away_score)
        home_losses = len(home_games) - home_wins
        away_wins = sum(1 for g in away_games if g.away_score > g.home_score)
        away_losses = len(away_games) - away_wins
        
        with col1:
            st.metric("Overall Record", f"{celtics_wins}-{celtics_losses}")
            st.metric("Win Percentage", f"{(celtics_wins/total_games)*100:.1f}%")
        
        with col2:
            st.metric("Home Record", f"{home_wins}-{home_losses}")
            st.metric("Home Win %", f"{(home_wins/len(home_games)*100 if home_games else 0):.1f}%")
            
        with col3:
            st.metric("Away Record", f"{away_wins}-{away_losses}")
            st.metric("Away Win %", f"{(away_wins/len(away_games)*100 if away_games else 0):.1f}%")

        # Season Records
        st.subheader("Record by Season")
        season_records = {}
        for game in games:
            season = game.season
            if season not in season_records:
                season_records[season] = {"wins": 0, "losses": 0}
            celtics_won = (game.home_team == "Boston Celtics" and game.home_score > game.away_score) or \
                         (game.away_team == "Boston Celtics" and game.away_score > game.home_score)
            if celtics_won:
                season_records[season]["wins"] += 1
            else:
                season_records[season]["losses"] += 1
        
        season_data = []
        for season, record in sorted(season_records.items()):
            win_pct = (record["wins"]/(record["wins"] + record["losses"]))*100
            season_data.append({
                "Season": season,
                "Wins": record["wins"],
                "Losses": record["losses"],
                "Win %": f"{win_pct:.1f}%"
            })
        st.table(pd.DataFrame(season_data))

        # Most Common Opponents
        st.subheader("Most Common Opponents")
        opponent_records = {}
        for game in games:
            opponent = game.away_team if game.home_team == "Boston Celtics" else game.home_team
            if opponent not in opponent_records:
                opponent_records[opponent] = {"games": 0, "wins": 0, "losses": 0}
            opponent_records[opponent]["games"] += 1
            celtics_won = (game.home_team == "Boston Celtics" and game.home_score > game.away_score) or \
                         (game.away_team == "Boston Celtics" and game.away_score > game.home_score)
            if celtics_won:
                opponent_records[opponent]["wins"] += 1
            else:
                opponent_records[opponent]["losses"] += 1
        
        opponent_data = []
        for opponent, record in sorted(opponent_records.items(), key=lambda x: x[1]["games"], reverse=True):
            win_pct = (record["wins"]/(record["games"]))*100
            opponent_data.append({
                "Opponent": opponent,
                "Games": record["games"],
                "Record": f"{record['wins']}-{record['losses']}",
                "Win %": f"{win_pct:.1f}%"
            })
        st.table(pd.DataFrame(opponent_data))

        # Away Game Venues
        st.subheader("Away Game Venues")
        venue_records = {}
        
        # Join Game with VenueInfo to get arena information
        games_with_venues = (
            session.query(Game, VenueInfo)
            .join(VenueInfo, Game.game_id == VenueInfo.game_id)
            .all()
        )
        
        for game, venue_info in games_with_venues:
            if game.away_team == "Boston Celtics":
                venue = f"{game.home_team} - {venue_info.arena}"
                if venue not in venue_records:
                    venue_records[venue] = {"games": 0, "wins": 0}
                venue_records[venue]["games"] += 1
                if game.away_score > game.home_score:
                    venue_records[venue]["wins"] += 1
        
        venue_data = []
        for venue, record in sorted(venue_records.items(), key=lambda x: x[1]["games"], reverse=True):
            win_pct = (record["wins"]/(record["games"]))*100
            venue_data.append({
                "Venue": venue,
                "Games": record["games"],
                "Wins": record["wins"],
                "Win %": f"{win_pct:.1f}%"
            })
        st.table(pd.DataFrame(venue_data))

        # Game Duration Stats
        st.subheader("Game Duration Statistics")
        col1, col2 = st.columns(2)
        
        # Get durations from venue_info
        games_with_duration = (
            session.query(Game, VenueInfo)
            .join(VenueInfo, Game.game_id == VenueInfo.game_id)
            .filter(VenueInfo.duration_minutes.isnot(None))
            .all()
        )
        
        if games_with_duration:
            durations = [venue.duration_minutes for _, venue in games_with_duration]
            total_minutes = sum(durations)
            avg_minutes = total_minutes / len(durations)
            
            with col1:
                st.metric("Total Minutes Watched", f"{total_minutes:,.0f}")
            with col2:
                st.metric("Average Game Duration", f"{avg_minutes:.0f} minutes")

        # Attendance Stats
        st.subheader("Attendance Statistics")
        attendances = [venue_info.attendance for game in games if venue_info.attendance]
        if attendances:
            avg_attendance = sum(attendances) / len(attendances)
            total_attendance = sum(attendances)
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Attendance", f"{avg_attendance:,.0f}")
            with col2:
                st.metric("Total Attendance", f"{total_attendance:,.0f}")

        # Streaks and Patterns
        st.subheader("Streaks and Patterns")
        
        # Sort games by date for streak analysis
        sorted_games = sorted(games, key=lambda x: x.date)
        current_streak = 0
        max_win_streak = 0
        max_lose_streak = 0
        current_win_streak = 0
        current_lose_streak = 0
        
        for game in sorted_games:
            celtics_won = (game.home_team == "Boston Celtics" and game.home_score > game.away_score) or \
                         (game.away_team == "Boston Celtics" and game.away_score > game.home_score)
            
            if celtics_won:
                current_streak = max(1, current_streak + 1)
                current_win_streak = current_streak
                current_lose_streak = 0
                max_win_streak = max(max_win_streak, current_streak)
            else:
                current_streak = min(-1, current_streak - 1)
                current_lose_streak = -current_streak
                current_win_streak = 0
                max_lose_streak = max(max_lose_streak, -current_streak)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Longest Win Streak", str(max_win_streak))
        with col2:
            st.metric("Longest Losing Streak", str(max_lose_streak))
        with col3:
            streak_text = f"{current_win_streak} wins" if current_win_streak > 0 else f"{current_lose_streak} losses"
            st.metric("Current Streak", streak_text)

        # Scoring Patterns
        st.subheader("Scoring Patterns")
        
        close_games = []
        blowouts = []
        celtics_100_plus = []
        celtics_110_plus = []
        celtics_120_plus = []
        overtime_games = []
        
        for game in games:
            celtics_score = game.home_score if game.home_team == "Boston Celtics" else game.away_score
            opponent_score = game.away_score if game.home_team == "Boston Celtics" else game.home_score
            point_diff = abs(game.home_score - game.away_score)
            
            # Check for close games and blowouts
            if point_diff <= 5:
                close_games.append(game)
            if point_diff >= 15:
                blowouts.append(game)
                
            # Check for high scoring games
            if celtics_score >= 100:
                celtics_100_plus.append(game)
            if celtics_score >= 110:
                celtics_110_plus.append(game)
            if celtics_score >= 120:
                celtics_120_plus.append(game)
            
            # Check for overtime games using QuarterScores
            ot_periods = [qs for qs in game.quarter_scores if qs.period.startswith('OT')]
            if ot_periods:
                overtime_games.append(game)
        
        scoring_data = []
        for category, games_list in [
            ("Close Games (≤5 pts)", close_games),
            ("Blowouts (≥15 pts)", blowouts),
            ("Scoring 100+", celtics_100_plus),
            ("Scoring 110+", celtics_110_plus),
            ("Scoring 120+", celtics_120_plus),
            ("Overtime Games", overtime_games)
        ]:
            wins = sum(1 for g in games_list if 
                (g.home_team == "Boston Celtics" and g.home_score > g.away_score) or
                (g.away_team == "Boston Celtics" and g.away_score > g.home_score))
            
            if games_list:
                win_pct = (wins/len(games_list))*100
                scoring_data.append({
                    "Category": category,
                    "Record": f"{wins}-{len(games_list)-wins}",
                    "Games": len(games_list),
                    "Win %": f"{win_pct:.1f}%"
                })
        
        st.table(pd.DataFrame(scoring_data))

        # Quarter Analysis
        st.subheader("Quarter Analysis")
        
        quarter_records = {
            "After 1st": {"wins": 0, "total": 0},
            "At Halftime": {"wins": 0, "total": 0},
            "After 3rd": {"wins": 0, "total": 0}
        }
        
        biggest_comeback = 0
        biggest_lead_lost = 0
        
        for game in games:
            celtics_is_home = game.home_team == "Boston Celtics"
            quarters = sorted(game.quarter_scores, key=lambda x: x.period)
            
            # Track running score for each quarter
            celtics_running = 0
            opponent_running = 0
            max_deficit = 0
            max_lead = 0
            
            for q in quarters:
                if q.period.startswith('Q'):  # Only regular quarters
                    celtics_score = q.home_score if celtics_is_home else q.away_score
                    opponent_score = q.away_score if celtics_is_home else q.home_score
                    
                    celtics_running += celtics_score
                    opponent_running += opponent_score
                    
                    deficit = opponent_running - celtics_running
                    max_deficit = min(max_deficit, deficit)
                    max_lead = max(max_lead, -deficit)
                    
                    # Record quarter leads
                    if q.period == 'Q1':
                        quarter_records["After 1st"]["total"] += 1
                        if celtics_running > opponent_running:
                            quarter_records["After 1st"]["wins"] += 1
                    elif q.period == 'Q2':
                        quarter_records["At Halftime"]["total"] += 1
                        if celtics_running > opponent_running:
                            quarter_records["At Halftime"]["wins"] += 1
                    elif q.period == 'Q3':
                        quarter_records["After 3rd"]["total"] += 1
                        if celtics_running > opponent_running:
                            quarter_records["After 3rd"]["wins"] += 1
            
            # Update comeback/blown lead stats
            celtics_won = (celtics_is_home and game.home_score > game.away_score) or \
                         (not celtics_is_home and game.away_score > game.home_score)
            
            if celtics_won:
                biggest_comeback = max(biggest_comeback, -max_deficit)
            else:
                biggest_lead_lost = max(biggest_lead_lost, max_lead)
        
        quarter_data = []
        for period, record in quarter_records.items():
            if record["total"] > 0:
                win_pct = (record["wins"]/record["total"])*100
                quarter_data.append({
                    "When Leading": period,
                    "Record": f"{record['wins']}-{record['total']-record['wins']}",
                    "Games": record["total"],
                    "Win %": f"{win_pct:.1f}%"
                })
        
        st.table(pd.DataFrame(quarter_data))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Biggest Comeback Win", f"{biggest_comeback} pts")
        with col2:
            st.metric("Biggest Lead Lost", f"{biggest_lead_lost} pts")

    finally:
        session.close()

def show_test_data():
    """Test NBA API data retrieval."""
    st.header("Test NBA API")
    
    date = st.date_input(
        "Select Date",
        value=datetime.now() - timedelta(days=1)
    )
    
    if st.button("Get Games"):
        client = NBAApiClient()
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            games = client.get_games_for_date(date_str)
            
            if not games:
                st.info("No games found for this date")
            else:
                st.success(f"Found {len(games)} games!")
                
                for game in games:
                    st.subheader(f"{game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
                    
                    try:
                        detailed_stats = client.get_detailed_stats(game['game_id'])
                        
                        # Create three columns for layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Game Info")
                            st.write(f"Game ID: {game['game_id']}")
                            st.write(f"Arena: {game['arena']}")
                            st.write(f"Season: {format_season(detailed_stats['season'][:4])}")
                            if detailed_stats['national_tv']:
                                st.write(f"National TV: {detailed_stats['national_tv']}")
                            st.write(f"Attendance: {detailed_stats['attendance']:,}")
                            st.write(f"Duration: {detailed_stats['duration']}")
                            
                            st.write("\nTeam Records")
                            st.write(f"{game['home_team']}: {detailed_stats['home_team_wins']}-{detailed_stats['home_team_losses']}")
                            st.write(f"{game['away_team']}: {detailed_stats['away_team_wins']}-{detailed_stats['away_team_losses']}")
                            
                            st.write("\nSeason Series")
                            # Show pre-game record
                            st.write(f"Pre-Game Series Record: {detailed_stats['pregame_series_record']}")
                            if detailed_stats['pregame_series_leader']:
                                leader_name = detailed_stats['pregame_series_leader']
                                if leader_name == game['home_team']:
                                    leader_name = game['home_team']
                                elif leader_name == game['away_team']:
                                    leader_name = game['away_team']
                                st.write(f"Pre-Game Series Leader: {leader_name}")
                            
                            # Show current record
                            st.write(f"Current Series Record: {detailed_stats['home_team_series_wins']}-{detailed_stats['home_team_series_losses']}")
                            if detailed_stats['series_leader']:
                                leader_name = detailed_stats['series_leader']
                                if leader_name == game['home_team']:
                                    leader_name = game['home_team']
                                elif leader_name == game['away_team']:
                                    leader_name = game['away_team']
                                st.write(f"Current Series Leader: {leader_name}")
                        
                        with col2:
                            st.write("Last Meeting")
                            last_meeting_date = datetime.strptime(detailed_stats['last_meeting_game_date'], '%Y-%m-%dT%H:%M:%S')
                            st.write(f"Game ID: {detailed_stats['last_meeting_game_id']}")
                            st.write(f"Date: {last_meeting_date.strftime('%Y-%m-%d')}")
                            st.write(f"{detailed_stats['last_meeting_visitor_city']} {detailed_stats['last_meeting_visitor_name']} ({detailed_stats['last_meeting_visitor_points']}) @ {detailed_stats['last_meeting_home_city']} {detailed_stats['last_meeting_home_name']} ({detailed_stats['last_meeting_home_points']})")
                        
                        # Display quarter scores in a DataFrame
                        st.write("\nQuarter Scores")
                        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                        home_scores = [detailed_stats[f'home_q{i}'] for i in range(1, 5)]
                        away_scores = [detailed_stats[f'away_q{i}'] for i in range(1, 5)]
                        
                        # Add overtime periods if they exist
                        ot = 1
                        while f'home_ot{ot}' in detailed_stats:
                            quarters.append(f'OT{ot}')
                            home_scores.append(detailed_stats[f'home_ot{ot}'])
                            away_scores.append(detailed_stats[f'away_ot{ot}'])
                            ot += 1
                        
                        # Add final score
                        quarters.append('Final')
                        home_scores.append(game['home_score'])
                        away_scores.append(game['away_score'])
                        
                        score_df = pd.DataFrame({
                            'Team': [game['home_team'], game['away_team']],
                            **{q: [h, a] for q, h, a in zip(quarters, home_scores, away_scores)}
                        })
                        st.dataframe(score_df, hide_index=True)
                        
                        # Display team stats in a DataFrame
                        st.write("\nTeam Stats")
                        stats_df = pd.DataFrame({
                            'Stat': [
                                'Points in Paint', 'Second Chance Points', 
                                'Fast Break Points', 'Team Turnovers',
                                'Total Turnovers', 'Team Rebounds', 'Points off Turnovers'
                            ],
                            game['home_team']: [
                                detailed_stats['home_paint_points'],
                                detailed_stats['home_second_chance_points'],
                                detailed_stats['home_fast_break_points'],
                                detailed_stats['home_team_turnovers'],
                                detailed_stats['home_total_turnovers'],
                                detailed_stats['home_team_rebounds'],
                                detailed_stats['home_points_off_to']
                            ],
                            game['away_team']: [
                                detailed_stats['away_paint_points'],
                                detailed_stats['away_second_chance_points'],
                                detailed_stats['away_fast_break_points'],
                                detailed_stats['away_team_turnovers'],
                                detailed_stats['away_total_turnovers'],
                                detailed_stats['away_team_rebounds'],
                                detailed_stats['away_points_off_to']
                            ]
                        })
                        st.dataframe(stats_df, hide_index=True)
                        
                        # Display game flow stats
                        st.write("\nGame Flow")
                        st.write(f"Lead Changes: {detailed_stats['lead_changes']}")
                        st.write(f"Times Tied: {detailed_stats['times_tied']}")
                        
                        # Display officials
                        st.write("\nOfficials")
                        for official in detailed_stats['officials_complete']:
                            st.write(f"{official['first_name']} {official['last_name']} (#{official['jersey_num'].strip()})")
                        
                        # Display inactive players
                        st.write("\nInactive Players")
                        for player in detailed_stats['inactive_players']:
                            st.write(f"{player['first_name']} {player['last_name']} (#{player['jersey_num'].strip()}) - {player['team_abbrev']}")
                        
                        st.markdown("---")  # Add a divider between games
                        
                    except Exception as e:
                        st.error(f"Error getting detailed stats: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

def show_database_preview():
    """Show a preview of the database structure and contents."""
    st.header("Database Preview")
    
    # Add table selection
    table_options = {
        "Games": Game,
        "Venue Info": VenueInfo,
        "Game Flow": GameFlow,
        "Quarter Scores": QuarterScores,
        "Team Stats": TeamStats,
        "Series Stats": SeriesStats,
        "Last Meetings": LastMeeting,
        "Officials": Official,
        "Inactive Players": InactivePlayer,
        "Photos": Photo,
        "Player Advanced Stats": PlayerAdvancedStats,
        "Team Advanced Stats": TeamAdvancedStats
    }
    
    selected_table = st.selectbox("Select Table", options=list(table_options.keys()))
    selected_model = table_options[selected_table]
    
    session = Session()
    try:
        # Get the most recent 20 records from selected table
        records = session.query(selected_model).order_by(selected_model.id.desc()).limit(20).all()
        
        # Create type row
        type_info = {}
        for column in selected_model.__table__.columns:
            if not column.name.startswith('_'):
                type_str = str(column.type).upper()
                
                if 'INTEGER' in type_str:
                    type_info[column.name] = "Integer"
                elif 'VARCHAR' in type_str or 'STRING' in type_str:
                    if '(' in type_str and ')' in type_str:
                        try:
                            length = type_str.split('(')[1].split(')')[0]
                            type_info[column.name] = f"String({length})"
                        except:
                            type_info[column.name] = "String"
                    else:
                        type_info[column.name] = "String"
                elif 'TEXT' in type_str:
                    type_info[column.name] = "Text"
                elif 'DATE' in type_str:
                    type_info[column.name] = "Date"
                elif 'TIME' in type_str:
                    type_info[column.name] = "Time"
                elif 'ENUM' in type_str:
                    type_info[column.name] = "Enum"
                else:
                    type_info[column.name] = str(column.type)
        
        # Convert records to list of dicts
        data = []
        for record in records:
            record_dict = {
                column.name: getattr(record, column.name)
                for column in selected_model.__table__.columns
                if not column.name.startswith('_')
            }
            data.append(record_dict)
        
        # Add type example as first row
        data.insert(0, type_info)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Display options
        st.subheader(f"Most Recent {selected_table} (with Data Types)")
        st.dataframe(df, use_container_width=True)
        
        # Show total column count
        st.info(f"Total number of columns: {len(df.columns)}")
        
    except Exception as e:
        st.error(f"Error loading database preview: {str(e)}")
    finally:
        session.close()

def view_database():
    """View and manage database entries."""
    st.header("Database Entries")
    
    # Get all games with their related data
    games = Session().query(Game).all()
    
    # Create tabs for different tables
    tabs = st.tabs([
        "Games", "Venue Info", "Game Flow", "Team Stats", 
        "Series Stats", "Last Meeting", "Quarter Scores", 
        "Officials", "Inactive Players", "Photos",
        "Player Advanced Stats", "Team Advanced Stats"
    ])
    
    # Games tab
    with tabs[0]:
        if games:
            games_data = []
            for game in games:
                games_data.append({
                    "ID": game.id,
                    "Game ID": game.game_id,
                    "Date": game.date,
                    "Home Team": game.home_team,
                    "Away Team": game.away_team,
                    "Score": f"{game.home_score}-{game.away_score}",
                    "Section": game.seat_section,
                    "Row": game.seat_row,
                    "Seat": game.seat_number
                })
            st.dataframe(games_data)
    
    # ... (existing tabs 1-9 remain the same) ...
    
    # Player Advanced Stats tab
    with tabs[10]:
        player_advanced_stats = Session().query(PlayerAdvancedStats).all()
        if player_advanced_stats:
            # Get column names from model
            columns = [column.key for column in inspect(PlayerAdvancedStats).attrs]
            
            player_adv_data = []
            for stat in player_advanced_stats:
                row_data = {}
                for col in columns:
                    row_data[col] = getattr(stat, col)
                player_adv_data.append(row_data)
            st.dataframe(player_adv_data)
    
    # Team Advanced Stats tab
    with tabs[11]:
        team_advanced_stats = Session().query(TeamAdvancedStats).all()
        if team_advanced_stats:
            # Get column names from model
            columns = [column.key for column in inspect(TeamAdvancedStats).attrs]
            
            team_adv_data = []
            for stat in team_advanced_stats:
                row_data = {}
                for col in columns:
                    row_data[col] = getattr(stat, col)
                team_adv_data.append(row_data)
            st.dataframe(team_adv_data)

if __name__ == "__main__":
    main()
