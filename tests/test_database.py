import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
            seat_section="Loge 12",
            seat_row="7",
            seat_number="15",
            ticket_price=150.00,
            attended_with="Family",
            notes="Great game!",
            weather="Clear, 72°F"
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
            away_score=98
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

if __name__ == '__main__':
    unittest.main() 