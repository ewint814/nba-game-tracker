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
from nba_api.stats.endpoints import boxscoreadvancedv2

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
                            player_stats = advanced_data['resultSets'][0]['rowSet']  # Player Stats
                            for player in player_stats:
                                # Get comment field and determine if player was a starter
                                starting_position = player[7]  # COMMENT field
                                starter = bool(starting_position and starting_position in ['F', 'G', 'C'])
                                
                                # Get status and determine if player played based on if they have stats
                                status = player[8] if player[8] and player[8].strip() else None  # COMMENT field
                                played = status is None
                                
                                def convert_stat(value):
                                    if value is None or (isinstance(value, (int, float)) and value == 0.0):
                                        return None
                                    return float(value)
                                
                                player_advanced = PlayerAdvancedStats(
                                    game_id=str(game_data['game_id']),
                                    team_id=player[1],
                                    player_id=player[4],
                                    player_name=player[5],
                                    starting_position=starting_position if starter else None,
                                    starter=starter,
                                    status=status,
                                    played=played,
                                    e_off_rating=convert_stat(player[10]),
                                    off_rating=convert_stat(player[11]),
                                    e_def_rating=convert_stat(player[12]),
                                    def_rating=convert_stat(player[13]),
                                    e_net_rating=convert_stat(player[14]),
                                    net_rating=convert_stat(player[15]),
                                    ast_pct=convert_stat(player[16]),
                                    ast_tov=convert_stat(player[17]),
                                    ast_ratio=convert_stat(player[18]),
                                    oreb_pct=convert_stat(player[19]),
                                    dreb_pct=convert_stat(player[20]),
                                    reb_pct=convert_stat(player[21]),
                                    tov_ratio=convert_stat(player[22]),
                                    efg_pct=convert_stat(player[23]),
                                    ts_pct=convert_stat(player[24]),
                                    usg_pct=convert_stat(player[25]),
                                    e_usg_pct=convert_stat(player[26]),
                                    e_pace=convert_stat(player[27]),
                                    pace=convert_stat(player[28]),
                                    pace_per40=convert_stat(player[29]),
                                    poss=convert_stat(player[30]),
                                    pie=convert_stat(player[31])
                                )
                                session.add(player_advanced)
                            
                            # Create team advanced stats
                            team_stats = advanced_data['resultSets'][1]['rowSet']  # Team Stats
                            for team in team_stats:
                                team_advanced = TeamAdvancedStats(
                                    game_id=str(game_data['game_id']),
                                    team_id=team[1],
                                    team_name=team[2],
                                    team_abbreviation=team[3],
                                    team_city=team[4],
                                    minutes=team[5],
                                    e_off_rating=team[6],
                                    off_rating=team[7],
                                    e_def_rating=team[8],
                                    def_rating=team[9],
                                    e_net_rating=team[10],
                                    net_rating=team[11],
                                    ast_pct=team[12],
                                    ast_tov=team[13],
                                    ast_ratio=team[14],
                                    oreb_pct=team[15],
                                    dreb_pct=team[16],
                                    reb_pct=team[17],
                                    e_tm_tov_pct=team[18],
                                    tm_tov_pct=team[19],
                                    efg_pct=team[20],
                                    ts_pct=team[21],
                                    usg_pct=team[22],
                                    e_usg_pct=team[23],
                                    e_pace=team[24],
                                    pace=team[25],
                                    pace_per40=team[26],
                                    poss=team[27],
                                    pie=team[28]
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
    """Show statistics about attended games."""
    st.header("Statistics")
    
    session = Session()
    try:
        games = session.query(Game).all()
        
        if games:
            total_games = len(games)
            st.metric("Total Games Attended", total_games)
            
            # Add more statistics here
        else:
            st.info("Add some games to see statistics!")
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
