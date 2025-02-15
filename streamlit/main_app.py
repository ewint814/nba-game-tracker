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
        ["Add Game", "My Games", "Statistics", "Test API"]
    )
    
    if page == "Add Game":
        show_add_game()
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
                                away_largest_lead=detailed_stats['away_largest_lead']
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
                games = client.get_games_for_date(date_str)
                
                if not games:
                    st.info("No games found for this date")
                else:
                    st.success(f"Found {len(games)} games!")
                    
                    for game in games:
                        st.subheader(f"{game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
                        st.caption(f"Game ID: {game['game_id']}")
                        st.write(f"Arena: {game['arena']}")
                        
                        try:
                            detailed_stats = client.get_detailed_stats(game['game_id'])
                            
                            # Create quarters list and scores
                            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                            home_scores = [
                                detailed_stats['home_q1'],
                                detailed_stats['home_q2'],
                                detailed_stats['home_q3'],
                                detailed_stats['home_q4']
                            ]
                            away_scores = [
                                detailed_stats['away_q1'],
                                detailed_stats['away_q2'],
                                detailed_stats['away_q3'],
                                detailed_stats['away_q4']
                            ]
                            
                            # Add overtime periods if they exist
                            for ot in range(1, 11):
                                ot_key = f'home_ot{ot}'
                                if ot_key in detailed_stats:
                                    quarters.append(f'OT{ot}')
                                    home_scores.append(detailed_stats[f'home_ot{ot}'])
                                    away_scores.append(detailed_stats[f'away_ot{ot}'])
                            
                            # Add final score
                            quarters.append('Final')
                            home_scores.append(game['home_score'])
                            away_scores.append(game['away_score'])
                            
                            # Create and display score DataFrame
                            score_df = pd.DataFrame({
                                'Team': [game['home_team'], game['away_team']],
                                **{q: [h, a] for q, h, a in zip(quarters, home_scores, away_scores)}
                            })
                            st.dataframe(score_df, hide_index=True)
                            
                            # Display other stats
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Game Info:")
                                st.write(f"Attendance: {detailed_stats['attendance']:,}")
                                st.write(f"Duration: {detailed_stats['duration']}")
                                st.write(f"Officials: {detailed_stats['officials']}")
                            
                            with col2:
                                st.write("Team Stats:")
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
                        
                        st.markdown("---")
                    
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
                        st.caption(f"Game ID: {game.game_id}")
                        
                        # Create quarters list and scores
                        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                        home_scores = [game.home_q1, game.home_q2, game.home_q3, game.home_q4]
                        away_scores = [game.away_q1, game.away_q2, game.away_q3, game.away_q4]
                        
                        # Add overtime periods if they exist
                        for ot in range(1, 11):
                            home_ot = getattr(game, f'home_ot{ot}')
                            away_ot = getattr(game, f'away_ot{ot}')
                            if home_ot is not None and away_ot is not None and (home_ot > 0 or away_ot > 0):
                                quarters.append(f'OT{ot}')
                                home_scores.append(home_ot)
                                away_scores.append(away_ot)
                        
                        # Add final score
                        quarters.append('Final')
                        home_scores.append(game.home_score)
                        away_scores.append(game.away_score)
                        
                        # Create and display score DataFrame
                        score_df = pd.DataFrame({
                            'Team': [game.home_team, game.away_team],
                            **{q: [h, a] for q, h, a in zip(quarters, home_scores, away_scores)}
                        })
                        st.dataframe(score_df, hide_index=True)
                        
                        # Display other game info
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Game Info:")
                            st.write(f"Attendance: {game.attendance:,}")
                            st.write(f"Duration: {game.duration}")
                            st.write(f"Officials: {game.officials}")
                        
                        with col2:
                            st.write("Team Stats:")
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

if __name__ == "__main__":
    main()
