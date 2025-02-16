import sys
import os
import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our database models
from src.data.database_models import init_db, Game, Photo, Base

class TestDatabase(unittest.TestCase):
    """Test cases for database models and operations."""
    
    def setUp(self):
        """Set up test database before each test."""
        # Use an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        """Clean up after each test."""
        Base.metadata.drop_all(self.engine)
        self.session.close()
    
    def test_create_game(self):
        """Test creating and retrieving a game."""
        # Create a test game
        game = Game(
            date=date(2024, 5, 13),
            home_team="Boston Celtics",
            away_team="Miami Heat",
            home_score=110,
            away_score=98,
            arena="TD Garden",
            game_id="0022400999",
            home_team_id=1610612738,
            away_team_id=1610612748,
            home_team_abbrev="BOS",
            away_team_abbrev="MIA",
            season="2024-2025",
            seat_section="Loge 12",
            seat_row="7",
            seat_number="15",
            attended_with="Family",
            notes="Great game!"
        )
        
        # Add game to database
        self.session.add(game)
        self.session.commit()
        
        # Retrieve the game
        saved_game = self.session.query(Game).first()
        
        # Verify the data
        self.assertEqual(saved_game.home_team, "Boston Celtics")
        self.assertEqual(saved_game.away_team, "Miami Heat")
        self.assertEqual(saved_game.seat_section, "Loge 12")
    
    def test_add_photo(self):
        """Test adding a photo to a game."""
        # Create a game first
        game = Game(
            date=date(2024, 5, 13),
            home_team="Boston Celtics",
            away_team="Miami Heat",
            home_score=110,
            away_score=98,
            arena="TD Garden",
            game_id="0022400999",
            home_team_id=1610612738,
            away_team_id=1610612748,
            home_team_abbrev="BOS",
            away_team_abbrev="MIA",
            season="2024-2025"
        )
        self.session.add(game)
        self.session.commit()
        
        # Add a photo
        photo = Photo(
            game_id=game.id,
            file_path="/path/to/photo.jpg",
            caption="Great view from the seats!"
        )
        self.session.add(photo)
        self.session.commit()
        
        # Verify the relationship
        self.assertEqual(len(game.photos), 1)
        self.assertEqual(game.photos[0].caption, "Great view from the seats!")

    def test_series_data(self):
        """Test storing and retrieving series data."""
        print("\nTesting Series Data Storage")
        print("=" * 50)
        
        # Create a test game with series data
        game = Game(
            date=date(2025, 2, 12),
            home_team="New York Knicks",
            away_team="Atlanta Hawks",
            home_team_id=1610612752,
            away_team_id=1610612737,
            home_team_abbrev="NYK",
            away_team_abbrev="ATL",
            home_score=149,
            away_score=148,
            arena="Madison Square Garden",
            game_id="0022400773",
            season="2024-2025",
            
            # Post-game series data
            home_team_series_wins=2,
            home_team_series_losses=2,
            series_leader="Tied",
            
            # Pre-game series data
            pregame_home_team_series_wins=1,
            pregame_home_team_series_losses=2,
            pregame_series_leader="ATL",
            pregame_series_record="1-2"
        )
        
        # Add game to database
        self.session.add(game)
        self.session.commit()
        
        # Retrieve the game
        saved_game = self.session.query(Game).first()
        
        # Verify post-game series data
        print("\nPost-game Series Data:")
        self.assertEqual(saved_game.home_team_series_wins, 2)
        self.assertEqual(saved_game.home_team_series_losses, 2)
        self.assertEqual(saved_game.series_leader, "Tied")
        print(f"• Wins: {saved_game.home_team_series_wins}")
        print(f"• Losses: {saved_game.home_team_series_losses}")
        print(f"• Leader: {saved_game.series_leader}")
        
        # Verify pre-game series data
        print("\nPre-game Series Data:")
        self.assertEqual(saved_game.pregame_home_team_series_wins, 1)
        self.assertEqual(saved_game.pregame_home_team_series_losses, 2)
        self.assertEqual(saved_game.pregame_series_leader, "ATL")
        self.assertEqual(saved_game.pregame_series_record, "1-2")
        print(f"• Wins: {saved_game.pregame_home_team_series_wins}")
        print(f"• Losses: {saved_game.pregame_home_team_series_losses}")
        print(f"• Leader: {saved_game.pregame_series_leader}")
        print(f"• Record: {saved_game.pregame_series_record}")

if __name__ == '__main__':
    unittest.main() 