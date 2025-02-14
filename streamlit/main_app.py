import streamlit as st
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from src.data.basketball_reference_scraper import BasketballReferenceScraper
from src.data.database_models import Game, Photo, Base

# Initialize database connection
engine = create_engine('sqlite:///basketball_tracker.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def main():
    """Main function that sets up the Streamlit app structure."""
    st.title("Basketball Game Tracker")
    
    # Create sidebar navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Add Game", "My Games", "Statistics"])
    
    if page == "Add Game":
        show_add_game()
    elif page == "My Games":
        show_my_games()
    else:
        show_statistics()

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
        scraper = BasketballReferenceScraper()
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            html = scraper.get_games_for_date(date_str)
            games = scraper.parse_games(html)
            st.session_state.available_games = games
            
        except Exception as e:
            st.error(f"Error fetching games: {str(e)}")
    
    # Show game selection if games are available
    if st.session_state.available_games:
        game_options = [
            f"{game['Winner']} ({game['Winner Score']}) vs {game['Loser']} ({game['Loser Score']})"
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
                    # Get the selected game data
                    game_idx = game_options.index(selected_game)
                    game_data = st.session_state.available_games[game_idx]
                    
                    # Create new game in database
                    session = Session()
                    try:
                        new_game = Game(
                            date=date,
                            home_team=game_data['Winner'],  # Simplified - need to determine home/away
                            away_team=game_data['Loser'],
                            home_score=game_data['Winner Score'],
                            away_score=game_data['Loser Score'],
                            seat_section=seat_section,
                            seat_row=seat_row,
                            seat_number=seat_number,
                            attended_with=attended_with,
                            notes=notes
                        )
                        session.add(new_game)
                        session.commit()
                        st.success("Game added successfully!")
                    except Exception as e:
                        st.error(f"Error saving game: {str(e)}")
                    finally:
                        session.close()

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

if __name__ == "__main__":
    main()
