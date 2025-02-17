"""
Game Calculations Module

This module handles basketball-specific calculations and transformations
of game data, including series records, team performance metrics,
and other statistical calculations.
"""

__all__ = ['format_season', 'calculate_series_stats']

def format_season(season_start_year):
    """
    Convert a season start year to full season format.
    
    Args:
        season_start_year (str or int): Starting year of the season (e.g., "2024" or 2024)
        
    Returns:
        str: Formatted season string (e.g., "2024-2025")
        
    Examples:
        >>> format_season("2024")
        "2024-2025"
        >>> format_season(2023)
        "2023-2024"
    """
    start_year = str(season_start_year)
    end_year = str(int(start_year) + 1)
    return f"{start_year}-{end_year}"

def calculate_series_stats(home_score, away_score, postgame_home_wins, postgame_home_losses, postgame_leader,
                         home_team_abbrev, away_team_abbrev):
    """
    Calculate pre-game series statistics based on post-game data.
    
    Args:
        home_score (int): Final home team score
        away_score (int): Final away team score
        postgame_home_wins (int): Home team series wins after this game
        postgame_home_losses (int): Home team series losses after this game
        postgame_leader (str): Series leader after this game (team abbreviation)
        home_team_abbrev (str): Home team abbreviation
        away_team_abbrev (str): Away team abbreviation
        
    Returns:
        dict: Dictionary containing pre-game series statistics
    """
    # Determine if this game's result is included in the postgame stats
    game_counted = (home_score > away_score and postgame_home_wins > 0) or (away_score > home_score and postgame_home_losses > 0)
    
    # Calculate pre-game stats by removing this game's result if needed
    if game_counted:
        if home_score > away_score:
            pregame_home_wins = postgame_home_wins - 1
            pregame_home_losses = postgame_home_losses
        else:
            pregame_home_wins = postgame_home_wins
            pregame_home_losses = postgame_home_losses - 1
    else:
        pregame_home_wins = postgame_home_wins
        pregame_home_losses = postgame_home_losses
    
    # Determine pre-game leader
    if pregame_home_wins > pregame_home_losses:
        pregame_leader = home_team_abbrev
    elif pregame_home_wins < pregame_home_losses:
        pregame_leader = away_team_abbrev
    else:
        pregame_leader = "Tied"
    
    # Format pre-game series record
    pregame_series_record = f"{pregame_home_wins}-{pregame_home_losses}"
    
    return {
        'pregame_home_wins': pregame_home_wins,
        'pregame_home_losses': pregame_home_losses,
        'pregame_leader': pregame_leader,
        'pregame_series_record': pregame_series_record
    } 