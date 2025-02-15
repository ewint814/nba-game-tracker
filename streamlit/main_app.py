import streamlit as st
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

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

def main():
    """Main function that sets up the Streamlit app structure."""
    st.title("Basketball Game Tracker")
    
    # Create sidebar navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Add Game", "View Games", "My Games", "Statistics", "Test API"]
    )
    
    if page == "Add Game":
        show_add_game()
    elif page == "View Games":
        show_games()
    elif page == "My Games":
        show_my_games()
    elif page == "Statistics":
        show_statistics()
    elif page == "Test API":
        show_test_data()

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
                                home_q1=detailed_stats['home_q1'],
                                home_q2=detailed_stats['home_q2'],
                                home_q3=detailed_stats['home_q3'],
                                home_q4=detailed_stats['home_q4'],
                                away_q1=detailed_stats['away_q1'],
                                away_q2=detailed_stats['away_q2'],
                                away_q3=detailed_stats['away_q3'],
                                away_q4=detailed_stats['away_q4'],
                                home_paint_points=detailed_stats['home_paint_points'],
                                away_paint_points=detailed_stats['away_paint_points'],
                                home_second_chance_points=detailed_stats['home_second_chance_points'],
                                away_second_chance_points=detailed_stats['away_second_chance_points'],
                                home_fast_break_points=detailed_stats['home_fast_break_points'],
                                away_fast_break_points=detailed_stats['away_fast_break_points'],
                                home_largest_lead=detailed_stats['home_largest_lead'],
                                away_largest_lead=detailed_stats['away_largest_lead']
                            )
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
    """Test NBA API data retrieval and database storage."""
    st.header("Test NBA API")
    
    # Add tabs for different test views
    tab1, tab2 = st.tabs(["Test API Calls", "View Saved Test Data"])
    
    with tab1:
        date = st.date_input(
            "Select Date",
            value=datetime.now() - timedelta(days=1)
        )
        
        if st.button("Get Games"):
            client = NBAApiClient()
            date_str = date.strftime("%Y-%m-%d")
            
            try:
                # Get basic game info
                games = client.get_games_for_date(date_str)
                
                if not games:
                    st.info("No games found for this date")
                else:
                    st.success(f"Found {len(games)} games!")
                    
                    # Display each game
                    for game in games:
                        st.subheader(f"{game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
                        st.write(f"Arena: {game['arena']}")
                        st.write(f"Game ID: {game['game_id']}")
                        
                        # Get and display detailed stats
                        try:
                            detailed_stats = client.get_detailed_stats(game['game_id'])
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("Game Info:")
                                st.write(f"Attendance: {detailed_stats['attendance']}")
                                st.write(f"Duration: {detailed_stats['duration']}")
                                st.write(f"Officials: {detailed_stats['officials']}")
                            
                            with col2:
                                st.write("Quarter Scores:")
                                st.write(f"{game['home_team']}: {detailed_stats['home_q1']} | {detailed_stats['home_q2']} | {detailed_stats['home_q3']} | {detailed_stats['home_q4']}")
                                st.write(f"{game['away_team']}: {detailed_stats['away_q1']} | {detailed_stats['away_q2']} | {detailed_stats['away_q3']} | {detailed_stats['away_q4']}")
                            
                            st.write("\nTeam Stats:")
                            stats_df = pd.DataFrame({
                                'Stat': ['Paint Points', 'Second Chance Points', 'Fast Break Points', 'Largest Lead'],
                                game['home_team']: [
                                    detailed_stats['home_paint_points'],
                                    detailed_stats['home_second_chance_points'],
                                    detailed_stats['home_fast_break_points'],
                                    detailed_stats['home_largest_lead']
                                ],
                                game['away_team']: [
                                    detailed_stats['away_paint_points'],
                                    detailed_stats['away_second_chance_points'],
                                    detailed_stats['away_fast_break_points'],
                                    detailed_stats['away_largest_lead']
                                ]
                            })
                            st.dataframe(stats_df, hide_index=True)
                            
                        except Exception as e:
                            st.error(f"Error getting detailed stats: {str(e)}")
                        
                        st.markdown("---")  # Separator between games
                    
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
    
    with tab2:
        st.subheader("Games in Database")
        session = Session()
        try:
            games = session.query(Game).order_by(Game.date.desc()).all()
            
            if not games:
                st.info("No games found in database")
            else:
                st.success(f"Found {len(games)} games!")
                
                for game in games:
                    with st.expander(f"{game.date.strftime('%Y-%m-%d')}: {game.away_team} @ {game.home_team}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Game Info:")
                            st.write(f"Attendance: {game.attendance:,}")
                            st.write(f"Duration: {game.duration}")
                            st.write(f"Officials: {game.officials}")
                        
                        with col2:
                            st.write("Quarter Scores:")
                            score_df = pd.DataFrame({
                                'Team': [game.home_team, game.away_team],
                                'Q1': [game.home_q1, game.away_q1],
                                'Q2': [game.home_q2, game.away_q2],
                                'Q3': [game.home_q3, game.away_q3],
                                'Q4': [game.home_q4, game.away_q4],
                                'Final': [game.home_score, game.away_score]
                            })
                            st.dataframe(score_df, hide_index=True)
                        
                        st.write("\nTeam Stats:")
                        stats_df = pd.DataFrame({
                            'Stat': ['Paint Points', 'Second Chance Points', 'Fast Break Points', 'Largest Lead'],
                            game.home_team: [
                                game.home_paint_points,
                                game.home_second_chance_points,
                                game.home_fast_break_points,
                                game.home_largest_lead
                            ],
                            game.away_team: [
                                game.away_paint_points,
                                game.away_second_chance_points,
                                game.away_fast_break_points,
                                game.away_largest_lead
                            ]
                        })
                        st.dataframe(stats_df, hide_index=True)
                        
        except Exception as e:
            st.error(f"Error loading games: {str(e)}")
        finally:
            session.close()

def show_games():
    """Display all attended games."""
    st.header("View Games")
    
    session = Session()
    try:
        games = session.query(Game).order_by(Game.date.desc()).all()
        
        if not games:
            st.info("No games found in database")
        else:
            st.success(f"Found {len(games)} games!")
            
            for game in games:
                st.subheader(f"{game.away_team} ({game.away_score}) @ {game.home_team} ({game.home_score})")
                st.write(f"Date: {game.date.strftime('%Y-%m-%d')}")
                st.write(f"Arena: {game.arena}")
                
                # Personal Details
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Seat Info:")
                    st.write(f"Section: {game.seat_section}")
                    st.write(f"Row: {game.seat_row}")
                    st.write(f"Seat: {game.seat_number}")
                    if game.attended_with:
                        st.write(f"Attended with: {game.attended_with}")
                
                with col2:
                    st.write("Game Info:")
                    st.write(f"Attendance: {game.attendance:,}")
                    st.write(f"Duration: {game.duration}")
                    st.write(f"Officials: {game.officials}")
                
                # Quarter Scores
                st.write("\nQuarter Scores:")
                score_df = pd.DataFrame({
                    'Team': [game.home_team, game.away_team],
                    'Q1': [game.home_q1, game.away_q1],
                    'Q2': [game.home_q2, game.away_q2],
                    'Q3': [game.home_q3, game.away_q3],
                    'Q4': [game.home_q4, game.away_q4],
                    'Final': [game.home_score, game.away_score]
                })
                st.dataframe(score_df, hide_index=True)
                
                # Team Stats
                st.write("\nTeam Stats:")
                stats_df = pd.DataFrame({
                    'Stat': ['Paint Points', 'Second Chance Points', 'Fast Break Points', 'Largest Lead'],
                    game.home_team: [
                        game.home_paint_points,
                        game.home_second_chance_points,
                        game.home_fast_break_points,
                        game.home_largest_lead
                    ],
                    game.away_team: [
                        game.away_paint_points,
                        game.away_second_chance_points,
                        game.away_fast_break_points,
                        game.away_largest_lead
                    ]
                })
                st.dataframe(stats_df, hide_index=True)
                
                if game.notes:
                    st.write("\nNotes:")
                    st.write(game.notes)
                
                # Show photos if any
                if game.photos:
                    st.write("\nPhotos:")
                    for photo in game.photos:
                        st.image(photo.file_path, caption=photo.caption)
                
                st.markdown("---")  # Separator between games
                
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
