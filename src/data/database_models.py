from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Text, Time, Enum, CheckConstraint, Interval, Boolean
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

    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), unique=True, nullable=False)
    date = Column(Date, nullable=False)
    season = Column(String(7))  # e.g., "2023-24"
    
    # Team Information
    home_team = Column(String(50))
    away_team = Column(String(50))
    home_team_id = Column(Integer)
    away_team_id = Column(Integer)
    home_team_abbrev = Column(String(3))
    away_team_abbrev = Column(String(3))
    
    # Score
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    # Personal attendance details (keeping for now)
    seat_section = Column(String(20))
    seat_row = Column(String(10))
    seat_number = Column(String(10))
    attended_with = Column(String(200))
    notes = Column(Text)
    
    # Relationships
    venue_info = relationship("VenueInfo", back_populates="game", uselist=False)
    game_flow = relationship("GameFlow", back_populates="game", uselist=False)
    team_stats = relationship("TeamStats", back_populates="game")
    series_stats = relationship("SeriesStats", back_populates="game")
    last_meeting = relationship("LastMeeting", back_populates="game")
    quarter_scores = relationship("QuarterScores", back_populates="game")
    officials = relationship("Official", back_populates="game")
    inactive_players = relationship("InactivePlayer", back_populates="game")
    photos = relationship("Photo", back_populates="game")

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

class Official(Base):
    __tablename__ = 'officials'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    official_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    jersey_num = Column(Integer, nullable=False)
    
    # Relationship to game
    game = relationship("Game", back_populates="officials")

class QuarterScores(Base):
    __tablename__ = 'quarter_scores'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    period = Column(String(3), nullable=False)  # Q1, Q2, Q3, Q4, OT1, OT2, etc.
    home_team_id = Column(Integer, nullable=False)
    away_team_id = Column(Integer, nullable=False)
    home_score = Column(Integer, CheckConstraint('home_score >= 0'))
    away_score = Column(Integer, CheckConstraint('away_score >= 0'))
    
    game = relationship("Game", back_populates="quarter_scores")

class TeamStats(Base):
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    team_id = Column(Integer, nullable=False)
    paint_points = Column(Integer, CheckConstraint('paint_points >= 0'))
    second_chance_points = Column(Integer, CheckConstraint('second_chance_points >= 0'))
    fast_break_points = Column(Integer, CheckConstraint('fast_break_points >= 0'))
    team_turnovers = Column(Integer, CheckConstraint('team_turnovers >= 0'))
    total_turnovers = Column(Integer, CheckConstraint('total_turnovers >= 0'))
    team_rebounds = Column(Integer, CheckConstraint('team_rebounds >= 0'))
    points_off_to = Column(Integer, CheckConstraint('points_off_to >= 0'))
    
    game = relationship("Game", back_populates="team_stats")

class SeriesStats(Base):
    __tablename__ = 'series_stats'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    
    # Pre-game series data
    pregame_home_team_series_wins = Column(Integer, CheckConstraint('pregame_home_team_series_wins >= 0'))
    pregame_home_team_series_losses = Column(Integer, CheckConstraint('pregame_home_team_series_losses >= 0'))
    pregame_series_leader = Column(String(3))
    pregame_series_record = Column(String(10))  # e.g., "2-1"
    
    # Post-game series data
    postgame_home_team_series_wins = Column(Integer, CheckConstraint('postgame_home_team_series_wins >= 0'))
    postgame_home_team_series_losses = Column(Integer, CheckConstraint('postgame_home_team_series_losses >= 0'))
    postgame_series_leader = Column(String(3))
    postgame_series_record = Column(String(10))  # e.g., "2-2"
    
    game = relationship("Game", back_populates="series_stats")

class LastMeeting(Base):
    __tablename__ = 'last_meetings'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    last_meeting_game_id = Column(String)
    last_meeting_game_date = Column(Date)
    home_team_id = Column(Integer)  # Renamed from team1_id
    away_team_id = Column(Integer)  # Renamed from team2_id
    home_team_score = Column(Integer)  # Renamed from team1_score
    away_team_score = Column(Integer)  # Renamed from team2_score
    
    game = relationship("Game", back_populates="last_meeting")

class VenueInfo(Base):
    __tablename__ = 'venue_info'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    arena = Column(String(100))
    attendance = Column(Integer)
    duration_minutes = Column(Integer)
    national_tv = Column(String(20))  # 'Local' or network name
    
    game = relationship("Game", back_populates="venue_info")

class GameFlow(Base):
    __tablename__ = 'game_flow'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(20), ForeignKey('games.game_id'), nullable=False)
    home_largest_lead = Column(Integer)
    away_largest_lead = Column(Integer)
    lead_changes = Column(Integer)
    times_tied = Column(Integer)
    
    game = relationship("Game", back_populates="game_flow")

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
