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
    
    # Game Details (from NBA API)
    home_team = Column(String(50), nullable=False)
    away_team = Column(String(50), nullable=False)
    home_score = Column(Integer)
    away_score = Column(Integer)
    arena = Column(String)
    game_id = Column(String)
    
    # Team Info
    home_team_id = Column(Integer)
    away_team_id = Column(Integer)
    home_team_abbrev = Column(String)
    away_team_abbrev = Column(String)
    
    # Basic Game Info
    season = Column(String)
    attendance = Column(Integer)
    duration = Column(String(20))
    national_tv = Column(String)
    
    # Team Records
    home_team_wins = Column(Integer)
    home_team_losses = Column(Integer)
    away_team_wins = Column(Integer)
    away_team_losses = Column(Integer)
    
    # Season Series
    home_team_series_wins = Column(Integer)
    home_team_series_losses = Column(Integer)
    series_leader = Column(String)
    
    # Season Series (pre-game)
    pregame_home_team_series_wins = Column(Integer)
    pregame_home_team_series_losses = Column(Integer)
    pregame_series_leader = Column(String)
    pregame_series_record = Column(String)
    
    # Last Meeting
    last_meeting_game_id = Column(String)
    last_meeting_game_date = Column(String)
    last_meeting_home_team_id = Column(Integer)
    last_meeting_home_city = Column(String)
    last_meeting_home_name = Column(String)
    last_meeting_home_abbrev = Column(String)
    last_meeting_home_points = Column(Integer)
    last_meeting_visitor_team_id = Column(Integer)
    last_meeting_visitor_city = Column(String)
    last_meeting_visitor_name = Column(String)
    last_meeting_visitor_abbrev = Column(String)
    last_meeting_visitor_points = Column(Integer)
    
    # Game Stats
    home_q1 = Column(Integer)
    home_q2 = Column(Integer)
    home_q3 = Column(Integer)
    home_q4 = Column(Integer)
    away_q1 = Column(Integer)
    away_q2 = Column(Integer)
    away_q3 = Column(Integer)
    away_q4 = Column(Integer)
    
    # Overtime periods (up to 10)
    home_ot1 = Column(Integer)
    home_ot2 = Column(Integer)
    home_ot3 = Column(Integer)
    home_ot4 = Column(Integer)
    home_ot5 = Column(Integer)
    home_ot6 = Column(Integer)
    home_ot7 = Column(Integer)
    home_ot8 = Column(Integer)
    home_ot9 = Column(Integer)
    home_ot10 = Column(Integer)
    away_ot1 = Column(Integer)
    away_ot2 = Column(Integer)
    away_ot3 = Column(Integer)
    away_ot4 = Column(Integer)
    away_ot5 = Column(Integer)
    away_ot6 = Column(Integer)
    away_ot7 = Column(Integer)
    away_ot8 = Column(Integer)
    away_ot9 = Column(Integer)
    away_ot10 = Column(Integer)
    
    # Team Stats
    home_paint_points = Column(Integer)
    away_paint_points = Column(Integer)
    home_second_chance_points = Column(Integer)
    away_second_chance_points = Column(Integer)
    home_fast_break_points = Column(Integer)
    away_fast_break_points = Column(Integer)
    home_largest_lead = Column(Integer)
    away_largest_lead = Column(Integer)
    home_team_turnovers = Column(Integer)
    away_team_turnovers = Column(Integer)
    home_total_turnovers = Column(Integer)
    away_total_turnovers = Column(Integer)
    home_team_rebounds = Column(Integer)
    away_team_rebounds = Column(Integer)
    home_points_off_to = Column(Integer)
    away_points_off_to = Column(Integer)
    lead_changes = Column(Integer)
    times_tied = Column(Integer)
    
    # Game Details
    officials = Column(String)  # Stored as JSON string
    officials_complete = Column(String)  # Stored as JSON string
    inactive_players = Column(String)  # Stored as JSON string
    
    # User Input
    seat_section = Column(String(20))
    seat_row = Column(String(10))
    seat_number = Column(String(10))
    attended_with = Column(String(200))
    notes = Column(Text)
    
    # Relationship to photos - allows multiple photos per game
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
