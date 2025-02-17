from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Text, Time, Enum, CheckConstraint, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
import enum
from src.utils.game_calculations import format_season
from datetime import timedelta, time

Base = declarative_base()

class GameType(enum.Enum):
    REGULAR_SEASON = "Regular Season"
    PLAY_IN = "Play-In"
    PLAYOFFS = "Playoffs"
    PRESEASON = "Preseason"

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
    home_score = Column(Integer, CheckConstraint('home_score >= 0'))
    away_score = Column(Integer, CheckConstraint('away_score >= 0'))
    arena = Column(String(100), nullable=False)
    game_id = Column(String(20), unique=True, nullable=False)
    
    # Team Info
    home_team_id = Column(Integer, nullable=False)
    away_team_id = Column(Integer, nullable=False)
    home_team_abbrev = Column(String(3), nullable=False)
    away_team_abbrev = Column(String(3), nullable=False)
    
    # Basic Game Info
    season = Column(String(9), nullable=False)
    attendance = Column(Integer, CheckConstraint('attendance >= 0'))
    duration_minutes = Column(Integer, CheckConstraint('duration_minutes >= 0'))  # Total game duration in minutes
    national_tv = Column(String(10))
    
    # Team Records
    home_team_wins = Column(Integer, CheckConstraint('home_team_wins >= 0'))
    home_team_losses = Column(Integer, CheckConstraint('home_team_losses >= 0'))
    away_team_wins = Column(Integer, CheckConstraint('away_team_wins >= 0'))
    away_team_losses = Column(Integer, CheckConstraint('away_team_losses >= 0'))
    
    # Season Series
    home_team_series_wins = Column(Integer, CheckConstraint('home_team_series_wins >= 0'))
    home_team_series_losses = Column(Integer, CheckConstraint('home_team_series_losses >= 0'))
    series_leader = Column(String(3))
    
    # Season Series (pre-game)
    pregame_home_team_series_wins = Column(Integer, CheckConstraint('pregame_home_team_series_wins >= 0'))
    pregame_home_team_series_losses = Column(Integer, CheckConstraint('pregame_home_team_series_losses >= 0'))
    pregame_series_leader = Column(String(3))
    pregame_series_record = Column(String(10))
    
    # Simple last meeting fields
    last_meeting_game_id = Column(String)
    last_meeting_game_date = Column(Date)
    last_meeting_team1_id = Column(Integer)
    last_meeting_team2_id = Column(Integer)
    last_meeting_team1_score = Column(Integer)
    last_meeting_team2_score = Column(Integer)
    
    # Game Stats
    home_q1 = Column(Integer, CheckConstraint('home_q1 >= 0'))
    home_q2 = Column(Integer, CheckConstraint('home_q2 >= 0'))
    home_q3 = Column(Integer, CheckConstraint('home_q3 >= 0'))
    home_q4 = Column(Integer, CheckConstraint('home_q4 >= 0'))
    away_q1 = Column(Integer, CheckConstraint('away_q1 >= 0'))
    away_q2 = Column(Integer, CheckConstraint('away_q2 >= 0'))
    away_q3 = Column(Integer, CheckConstraint('away_q3 >= 0'))
    away_q4 = Column(Integer, CheckConstraint('away_q4 >= 0'))
    
    # Overtime Periods (nullable)
    home_ot1 = Column(Integer, CheckConstraint('home_ot1 >= 0'))
    home_ot2 = Column(Integer, CheckConstraint('home_ot2 >= 0'))
    home_ot3 = Column(Integer, CheckConstraint('home_ot3 >= 0'))
    home_ot4 = Column(Integer, CheckConstraint('home_ot4 >= 0'))
    home_ot5 = Column(Integer, CheckConstraint('home_ot5 >= 0'))
    home_ot6 = Column(Integer, CheckConstraint('home_ot6 >= 0'))
    home_ot7 = Column(Integer, CheckConstraint('home_ot7 >= 0'))
    home_ot8 = Column(Integer, CheckConstraint('home_ot8 >= 0'))
    home_ot9 = Column(Integer, CheckConstraint('home_ot9 >= 0'))
    home_ot10 = Column(Integer, CheckConstraint('home_ot10 >= 0'))
    
    away_ot1 = Column(Integer, CheckConstraint('away_ot1 >= 0'))
    away_ot2 = Column(Integer, CheckConstraint('away_ot2 >= 0'))
    away_ot3 = Column(Integer, CheckConstraint('away_ot3 >= 0'))
    away_ot4 = Column(Integer, CheckConstraint('away_ot4 >= 0'))
    away_ot5 = Column(Integer, CheckConstraint('away_ot5 >= 0'))
    away_ot6 = Column(Integer, CheckConstraint('away_ot6 >= 0'))
    away_ot7 = Column(Integer, CheckConstraint('away_ot7 >= 0'))
    away_ot8 = Column(Integer, CheckConstraint('away_ot8 >= 0'))
    away_ot9 = Column(Integer, CheckConstraint('away_ot9 >= 0'))
    away_ot10 = Column(Integer, CheckConstraint('away_ot10 >= 0'))
    
    # Team Stats
    home_paint_points = Column(Integer, CheckConstraint('home_paint_points >= 0'))
    away_paint_points = Column(Integer, CheckConstraint('away_paint_points >= 0'))
    home_second_chance_points = Column(Integer, CheckConstraint('home_second_chance_points >= 0'))
    away_second_chance_points = Column(Integer, CheckConstraint('away_second_chance_points >= 0'))
    home_fast_break_points = Column(Integer, CheckConstraint('home_fast_break_points >= 0'))
    away_fast_break_points = Column(Integer, CheckConstraint('away_fast_break_points >= 0'))
    home_largest_lead = Column(Integer)
    away_largest_lead = Column(Integer)
    home_team_turnovers = Column(Integer, CheckConstraint('home_team_turnovers >= 0'))
    away_team_turnovers = Column(Integer, CheckConstraint('away_team_turnovers >= 0'))
    home_total_turnovers = Column(Integer, CheckConstraint('home_total_turnovers >= 0'))
    away_total_turnovers = Column(Integer, CheckConstraint('away_total_turnovers >= 0'))
    home_team_rebounds = Column(Integer, CheckConstraint('home_team_rebounds >= 0'))
    away_team_rebounds = Column(Integer, CheckConstraint('away_team_rebounds >= 0'))
    home_points_off_to = Column(Integer, CheckConstraint('home_points_off_to >= 0'))
    away_points_off_to = Column(Integer, CheckConstraint('away_points_off_to >= 0'))
    lead_changes = Column(Integer, CheckConstraint('lead_changes >= 0'))
    times_tied = Column(Integer, CheckConstraint('times_tied >= 0'))
    
    # User Input
    seat_section = Column(String(20))
    seat_row = Column(String(10))
    seat_number = Column(String(10))
    attended_with = Column(String(200))
    notes = Column(Text)
    
    # Relationship to photos - allows multiple photos per game
    photos = relationship("Photo", back_populates="game")

    # Split officials into 3 columns each, making them nullable
    official1_id = Column(Integer, nullable=True)
    official1_name = Column(String, nullable=True)
    official1_number = Column(Integer, nullable=True)
    
    official2_id = Column(Integer, nullable=True)
    official2_name = Column(String, nullable=True)
    official2_number = Column(Integer, nullable=True)
    
    official3_id = Column(Integer, nullable=True)
    official3_name = Column(String, nullable=True)
    official3_number = Column(Integer, nullable=True)

    # Add relationship to inactive players
    inactive_players = relationship("InactivePlayer", back_populates="game")

    def __repr__(self):
        return f"<Game {self.date}: {self.away_team} @ {self.home_team}>"

    @validates('season')
    def validate_season(self, key, season):
        """Ensure season is in YYYY-YYYY format"""
        if '-' not in season:
            # If just given a year, convert to full format
            return format_season(season)
        return season

    @validates('duration_minutes')
    def validate_duration(self, key, duration_str):
        """Convert HH:MM format to total minutes"""
        if isinstance(duration_str, str):
            try:
                hours, minutes = map(int, duration_str.split(':'))
                return (hours * 60) + minutes
            except:
                return None
        return duration_str

class Photo(Base):
    """
    Stores photos from attended games.
    
    This model handles the storage of game photos, allowing multiple
    photos per game with optional captions. The actual image files
    are stored on disk, with this table storing the file paths.
    """
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)  # Links photo to specific game
    file_path = Column(String(500), nullable=False)    # Path to stored image file
    caption = Column(Text)                             # Optional photo description
    
    # Relationship back to the game
    game = relationship("Game", back_populates="photos")

    def __repr__(self):
        return f"<Photo {self.id} for Game {self.game_id}>"

class InactivePlayer(Base):
    __tablename__ = 'inactive_players'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    jersey_num = Column(Integer)
    team_id = Column(Integer, nullable=False)  # Changed from team_abbrev to team_id
    
    # Relationship to game using game_id
    game = relationship("Game", back_populates="inactive_players", foreign_keys=[game_id])

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
