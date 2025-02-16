"""
Game Calculations Module

This module handles basketball-specific calculations and transformations
of game data, including series records, team performance metrics,
and other statistical calculations.
"""

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
    # Calculate pre-game record by removing current game result
    if home_score > away_score:
        pregame_home_wins = postgame_home_wins - 1
        pregame_home_losses = postgame_home_losses
    else:
        pregame_home_wins = postgame_home_wins
        pregame_home_losses = postgame_home_losses - 1
    
    # Calculate pre-game leader
    if pregame_home_wins > pregame_home_losses:
        pregame_leader = home_team_abbrev
    elif pregame_home_wins < pregame_home_losses:
        pregame_leader = away_team_abbrev
    else:
        pregame_leader = None
        
    return {
        'pregame_home_wins': pregame_home_wins,
        'pregame_home_losses': pregame_home_losses,
        'pregame_leader': pregame_leader,
        'pregame_series_record': f"{pregame_home_wins}-{pregame_home_losses}"
    } 