"""
NBA API Client Module

This module provides a wrapper around the nba_api package to fetch game data,
statistics, and other NBA-related information.
"""

from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams
from datetime import datetime

class NBAApiClient:
    """A client for interacting with the NBA API with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize the NBA API client with team mapping."""
        # Create team ID to name mapping
        nba_teams = teams.get_teams()
        self.team_dict = {team['id']: team['full_name'] for team in nba_teams}
    
    def get_games_for_date(self, date_str):
        """
        Fetch all NBA games for a specific date.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            list: List of game dictionaries with basic information
        """
        try:
            # Convert string date to datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Get games from scoreboard
            board = scoreboardv2.ScoreboardV2(
                game_date=date_obj,
                league_id='00',
                day_offset=0
            )
            
            games = board.get_dict()
            game_data = games['resultSets'][0]['rowSet']
            
            # Format game data
            formatted_games = []
            for game in game_data:
                home_team_id = game[6]  # HOME_TEAM_ID
                visitor_team_id = game[7]  # VISITOR_TEAM_ID
                arena = game[15]  # ARENA_NAME
                game_id = game[2]  # GAME_ID
                
                formatted_game = {
                    'game_id': str(game_id),
                    'home_team': self.team_dict.get(home_team_id, f"Unknown Team ({home_team_id})"),
                    'away_team': self.team_dict.get(visitor_team_id, f"Unknown Team ({visitor_team_id})"),
                    'arena': arena,
                    'date': date_str
                }
                formatted_games.append(formatted_game)
            
            return formatted_games
            
        except Exception as e:
            print(f"Error in get_games_for_date: {str(e)}")
            raise

    def get_box_score(self, game_id):
        """
        Fetch detailed box score for a specific game.
        
        Args:
            game_id (str): NBA API game ID
            
        Returns:
            dict: Dictionary containing box score statistics
        """
        # TODO: Implement box score fetching when needed
        pass


if __name__ == "__main__":
    # Example usage
    client = NBAApiClient()
    
    # Test with a specific date
    test_date = "2025-02-10"
    print(f"\nGetting games for {test_date}:")
    
    try:
        games = client.get_games_for_date(test_date)
        print(f"\nFound {len(games)} games:")
        
        for game in games:
            print(f"\n{game['away_team']} @ {game['home_team']}")
            print(f"Arena: {game['arena']}")
            print(f"Game ID: {game['game_id']}")
    except Exception as e:
        print(f"Error: {str(e)}")
