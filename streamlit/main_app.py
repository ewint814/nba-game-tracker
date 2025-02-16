import streamlit as st
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from src.data.basketball_reference_scraper import BasketballReferenceScraper
from src.data.database_models import Game, Photo, Base
from src.data.nba_api_client import NBAApiClient

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
        # Remove existing database
        if os.path.exists('basketball_tracker.db'):
            os.remove('basketball_tracker.db')
            st.success("Existing database removed")
        
        # Create new database with current schema
        engine = create_engine('sqlite:///basketball_tracker.db')
        Base.metadata.create_all(engine)
        st.success("New database created with updated schema")
        
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
                            
                        # Create new game in database
                        session = Session()
                        try:
                            # Create new game instance with all data
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
                                arena=game_data['arena'],
                                game_id=game_data['game_id'],
                                # Add detailed stats
                                attendance=detailed_stats['attendance'],
                                duration=detailed_stats['duration'],
                                officials=detailed_stats['officials'],
                                officials_complete=json.dumps(detailed_stats['officials_complete']),
                                inactive_players=json.dumps(detailed_stats['inactive_players']),
                                # Quarter scores
                                home_q1=detailed_stats['home_q1'],
                                home_q2=detailed_stats['home_q2'],
                                home_q3=detailed_stats['home_q3'],
                                home_q4=detailed_stats['home_q4'],
                                away_q1=detailed_stats['away_q1'],
                                away_q2=detailed_stats['away_q2'],
                                away_q3=detailed_stats['away_q3'],
                                away_q4=detailed_stats['away_q4'],
                                # Team stats
                                home_paint_points=detailed_stats['home_paint_points'],
                                away_paint_points=detailed_stats['away_paint_points'],
                                home_second_chance_points=detailed_stats['home_second_chance_points'],
                                away_second_chance_points=detailed_stats['away_second_chance_points'],
                                home_fast_break_points=detailed_stats['home_fast_break_points'],
                                away_fast_break_points=detailed_stats['away_fast_break_points'],
                                home_largest_lead=detailed_stats['home_largest_lead'],
                                away_largest_lead=detailed_stats['away_largest_lead'],
                                # New fields
                                season=detailed_stats['season'],
                                national_tv=detailed_stats['national_tv'],
                                home_team_id=detailed_stats['home_team_id'],
                                away_team_id=detailed_stats['visitor_team_id'],
                                home_team_abbrev=detailed_stats['home_team_abbrev'],
                                away_team_abbrev=detailed_stats['away_team_abbrev'],
                                home_team_wins=detailed_stats['home_team_wins'],
                                home_team_losses=detailed_stats['home_team_losses'],
                                away_team_wins=detailed_stats['away_team_wins'],
                                away_team_losses=detailed_stats['away_team_losses'],
                                home_team_series_wins=detailed_stats['home_team_series_wins'],
                                home_team_series_losses=detailed_stats['home_team_series_losses'],
                                series_leader=detailed_stats['series_leader'],
                                last_meeting_game_id=detailed_stats['last_meeting_game_id'],
                                last_meeting_game_date=detailed_stats['last_meeting_game_date'],
                                last_meeting_home_team_id=detailed_stats['last_meeting_home_team_id'],
                                last_meeting_home_city=detailed_stats['last_meeting_home_city'],
                                last_meeting_home_name=detailed_stats['last_meeting_home_name'],
                                last_meeting_home_abbrev=detailed_stats['last_meeting_home_abbrev'],
                                last_meeting_home_points=detailed_stats['last_meeting_home_points'],
                                last_meeting_visitor_team_id=detailed_stats['last_meeting_visitor_team_id'],
                                last_meeting_visitor_city=detailed_stats['last_meeting_visitor_city'],
                                last_meeting_visitor_name=detailed_stats['last_meeting_visitor_name'],
                                last_meeting_visitor_abbrev=detailed_stats['last_meeting_visitor_abbrev'],
                                last_meeting_visitor_points=detailed_stats['last_meeting_visitor_points'],
                                home_team_turnovers=detailed_stats['home_team_turnovers'],
                                away_team_turnovers=detailed_stats['away_team_turnovers'],
                                home_total_turnovers=detailed_stats['home_total_turnovers'],
                                away_total_turnovers=detailed_stats['away_total_turnovers'],
                                home_team_rebounds=detailed_stats['home_team_rebounds'],
                                away_team_rebounds=detailed_stats['away_team_rebounds'],
                                home_points_off_to=detailed_stats['home_points_off_to'],
                                away_points_off_to=detailed_stats['away_points_off_to'],
                                lead_changes=detailed_stats['lead_changes'],
                                times_tied=detailed_stats['times_tied']
                            )

                            # Add overtime periods if they exist
                            for ot in range(1, 11):
                                ot_key = f'home_ot{ot}'
                                if ot_key in detailed_stats:
                                    setattr(new_game, f'home_ot{ot}', detailed_stats[f'home_ot{ot}'])
                                    setattr(new_game, f'away_ot{ot}', detailed_stats[f'away_ot{ot}'])

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
                        detailed = client.get_detailed_stats(game['game_id'])
                        
                        # Create three columns for layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Game Info")
                            st.write(f"Game ID: {game['game_id']}")
                            st.write(f"Arena: {game['arena']}")
                            season_start = detailed['season'][:4]
                            season_end = str(int(season_start) + 1)  # Add 1 to get the next year
                            st.write(f"Season: {season_start}-{season_end}")
                            if detailed['national_tv']:
                                st.write(f"National TV: {detailed['national_tv']}")
                            st.write(f"Attendance: {detailed['attendance']:,}")
                            st.write(f"Duration: {detailed['duration']}")
                            
                            st.write("\nTeam Records")
                            st.write(f"{game['home_team']}: {detailed['home_team_wins']}-{detailed['home_team_losses']}")
                            st.write(f"{game['away_team']}: {detailed['away_team_wins']}-{detailed['away_team_losses']}")
                            
                            st.write("\nSeason Series")
                            # Show pre-game record
                            st.write(f"Pre-Game Series Record: {detailed['pregame_series_record']}")
                            if detailed['pregame_series_leader']:
                                leader_name = detailed['pregame_series_leader']
                                if leader_name == game['home_team']:
                                    leader_name = game['home_team']
                                elif leader_name == game['away_team']:
                                    leader_name = game['away_team']
                                st.write(f"Pre-Game Series Leader: {leader_name}")
                            
                            # Show current record
                            st.write(f"Current Series Record: {detailed['home_team_series_wins']}-{detailed['home_team_series_losses']}")
                            if detailed['series_leader']:
                                leader_name = detailed['series_leader']
                                if leader_name == game['home_team']:
                                    leader_name = game['home_team']
                                elif leader_name == game['away_team']:
                                    leader_name = game['away_team']
                                st.write(f"Current Series Leader: {leader_name}")
                        
                        with col2:
                            st.write("Last Meeting")
                            last_meeting_date = datetime.strptime(detailed['last_meeting_game_date'], '%Y-%m-%dT%H:%M:%S')
                            st.write(f"Date: {last_meeting_date.strftime('%Y-%m-%d')}")
                            st.write(f"{detailed['last_meeting_visitor_city']} {detailed['last_meeting_visitor_name']} ({detailed['last_meeting_visitor_points']})")
                            st.write(f"{detailed['last_meeting_home_city']} {detailed['last_meeting_home_name']} ({detailed['last_meeting_home_points']})")
                        
                        # Display quarter scores in a DataFrame
                        st.write("\nQuarter Scores")
                        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                        home_scores = [detailed[f'home_q{i}'] for i in range(1, 5)]
                        away_scores = [detailed[f'away_q{i}'] for i in range(1, 5)]
                        
                        # Add overtime periods if they exist
                        ot = 1
                        while f'home_ot{ot}' in detailed:
                            quarters.append(f'OT{ot}')
                            home_scores.append(detailed[f'home_ot{ot}'])
                            away_scores.append(detailed[f'away_ot{ot}'])
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
                                'Fast Break Points', 'Largest Lead',
                                'Team Turnovers', 'Total Turnovers',
                                'Team Rebounds', 'Points off Turnovers'
                            ],
                            game['home_team']: [
                                detailed['home_paint_points'],
                                detailed['home_second_chance_points'],
                                detailed['home_fast_break_points'],
                                detailed['home_largest_lead'],
                                detailed['home_team_turnovers'],
                                detailed['home_total_turnovers'],
                                detailed['home_team_rebounds'],
                                detailed['home_points_off_to']
                            ],
                            game['away_team']: [
                                detailed['away_paint_points'],
                                detailed['away_second_chance_points'],
                                detailed['away_fast_break_points'],
                                detailed['away_largest_lead'],
                                detailed['away_team_turnovers'],
                                detailed['away_total_turnovers'],
                                detailed['away_team_rebounds'],
                                detailed['away_points_off_to']
                            ]
                        })
                        st.dataframe(stats_df, hide_index=True)
                        
                        # Display game flow stats
                        st.write("\nGame Flow")
                        st.write(f"Lead Changes: {detailed['lead_changes']}")
                        st.write(f"Times Tied: {detailed['times_tied']}")
                        
                        # Display officials
                        st.write("\nOfficials")
                        for official in detailed['officials_complete']:
                            st.write(f"{official['first_name']} {official['last_name']} (#{official['jersey_num'].strip()})")
                        
                        # Display inactive players
                        st.write("\nInactive Players")
                        for player in detailed['inactive_players']:
                            st.write(f"{player['first_name']} {player['last_name']} (#{player['jersey_num'].strip()}) - {player['team_abbrev']}")
                        
                        st.markdown("---")  # Add a divider between games
                        
                    except Exception as e:
                        st.error(f"Error getting detailed stats: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

def format_season(season):
    """Format season string as YYYY-YYYY."""
    start_year = season[:4]
    return f"{start_year}-{int(start_year) + 1}"

def show_database_preview():
    """Show a preview of the database structure and contents."""
    st.header("Database Preview")
    
    session = Session()
    try:
        # Get the most recent 20 games
        games = session.query(Game).order_by(Game.date.desc()).limit(20).all()
        
        # Convert games to list of dicts first
        games_data = []
        for game in games:
            game_dict = {
                column.name: getattr(game, column.name)
                for column in Game.__table__.columns
                if not column.name.startswith('_')
            }
            games_data.append(game_dict)
        
        # Create DataFrame first
        df = pd.DataFrame(games_data)
        
        # Create type row
        type_info = {}
        for column in Game.__table__.columns:
            if not column.name.startswith('_'):
                type_str = str(column.type).upper()
                
                if 'INTEGER' in type_str:
                    type_info[column.name] = "Integer"
                elif 'VARCHAR' in type_str or 'STRING' in type_str:
                    # Safely extract length if it exists
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
                    type_info[column.name] = type_str
        
        # Add type row at the top
        df = pd.concat([pd.DataFrame([type_info]), df], ignore_index=True)
        
        # Display options
        st.subheader("Most Recent Games (with Data Types)")
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                column: st.column_config.Column(
                    width="medium"
                ) for column in df.columns
            }
        )
        
        # Show total column count
        st.info(f"Total number of columns: {len(df.columns)}")
        
    except Exception as e:
        st.error(f"Error loading database preview: {str(e)}")
        # Debug info
        st.error("Debug info:")
        for column in Game.__table__.columns:
            st.write(f"Column: {column.name}, Type: {str(column.type)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
