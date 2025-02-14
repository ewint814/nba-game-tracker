from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Game(Base):
    """
    Represents a basketball game attended.
    Stores both the game data and personal attendance details.
    
    This model combines official game data (scraped from Basketball Reference)
    with personal details about attendance, creating a complete record of
    each game experience.
    """
    __tablename__ = 'games'

    # Primary key for unique game identification
    id = Column(Integer, primary_key=True)
    
    # When the game was played
    date = Column(Date, nullable=False)
    
    # Game Details (scraped from Basketball Reference)
    home_team = Column(String(50), nullable=False)  # e.g., "Boston Celtics"
    away_team = Column(String(50), nullable=False)  # e.g., "Los Angeles Lakers"
    home_score = Column(Integer)                    # Final score for home team
    away_score = Column(Integer)                    # Final score for away team
    
    # Personal Attendance Details
    seat_section = Column(String(20))   # e.g., "Loge 12", "Balcony 324"
    seat_row = Column(String(10))       # e.g., "7", "AA"
    seat_number = Column(String(10))    # e.g., "12", "3-4"
    ticket_price = Column(Float)        # How much paid for ticket(s)
    attended_with = Column(String(200)) # Who went to the game with you
    notes = Column(Text)                # Any personal notes about the game
    weather = Column(String(100))       # Weather conditions during game
    
    # Relationship to photos - allows multiple photos per game
    # Access using game.photos to get all photos for a game
    photos = relationship("Photo", back_populates="game")

class Photo(Base):
    """
    Stores photos from attended games.
    
    This model handles the storage of game photos, allowing multiple
    photos per game with optional captions. The actual image files
    are stored on disk, with this table storing the file paths.
    """
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))  # Links photo to specific game
    file_path = Column(String(500), nullable=False)    # Path to stored image file
    caption = Column(Text)                             # Optional photo description
    
    # Relationship back to the game
    # Access using photo.game to get the associated game
    game = relationship("Game", back_populates="photos")

def init_db(db_path='sqlite:///basketball_tracker.db'):
    """
    Initialize the database and create all tables.
    
    Args:
        db_path (str): SQLAlchemy database URL. Defaults to local SQLite database.
            Example: 'sqlite:///basketball_tracker.db'
            
    This function should be run once when setting up the application.
    It will create the database and all necessary tables if they don't exist.
    """
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
