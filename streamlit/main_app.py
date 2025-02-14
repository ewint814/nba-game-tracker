import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path so we can import our modules
# This is needed because we're running from a different directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom scraper class
from src.data.basketball_reference_scraper import BasketballReferenceScraper

def main():
    """Main function that sets up the Streamlit app structure."""
    st.title("Basketball Game Tracker")
    
    # Create sidebar navigation menu
    # This will always be visible and allows switching between pages
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Game Lookup", "My Games", "Statistics"])
    
    # Route to different pages based on navigation selection
    if page == "Game Lookup":
        show_game_lookup()
    elif page == "My Games":
        show_my_games()
    else:
        show_statistics()

def show_game_lookup():
    """
    Display the game lookup page.
    Allows users to search for games by date and filter by team.
    """
    st.header("Game Lookup")
    
    # Date input widget - defaults to yesterday as most recent games will be from then
    date = st.date_input(
        "Select Date",
        value=datetime.now() - timedelta(days=1)
    )
    
    # Optional team filter - defaults to Boston
    team = st.text_input("Team Filter (optional)", value="Boston")
    
    # Only fetch data when user clicks the button
    if st.button("Look up Games"):
        scraper = BasketballReferenceScraper()
        
        # Convert date to string format required by scraper
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            # Fetch and parse games using our scraper
            html = scraper.get_games_for_date(date_str)
            games = scraper.parse_games(html, team_filter=team if team else None)
            
            if games:
                # Display games if found
                st.subheader(f"Games on {date_str}")
                for game in games:
                    # Show each game with a basketball emoji for visual appeal
                    st.write(f"🏀 {game['Winner']} ({game['Winner Score']}) vs {game['Loser']} ({game['Loser Score']})")
                    # Add a button for each game to view more details (functionality coming soon)
                    if st.button(f"View Details for {game['Winner']} vs {game['Loser']}"):
                        st.write("Box score details coming soon!")
            else:
                # Show informative message if no games found
                st.info(f"No games found for {date_str}" + (f" with {team}" if team else ""))
        except Exception as e:
            # Handle any errors that occur during scraping
            st.error(f"Error fetching games: {str(e)}")

def show_my_games():
    """
    Placeholder for the My Games page.
    Will eventually show games the user has attended.
    """
    st.header("My Games")
    st.write("Coming soon: Track games you've attended!")

def show_statistics():
    """
    Placeholder for the Statistics page.
    Will eventually show analytics about games.
    """
    st.header("Statistics")
    st.write("Coming soon: View statistics about games!")

if __name__ == "__main__":
    main()
