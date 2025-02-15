"""
NBA API Client Module

This module provides a wrapper around the nba_api package to fetch game data,
statistics, and other NBA-related information.
"""

from nba_api.stats.endpoints import scoreboardv2, boxscoresummaryv2
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
            game_data = games['resultSets'][0]['rowSet']  # GameHeader
            line_score = games['resultSets'][1]['rowSet']  # LineScore has the scores
            
            formatted_games = []
            for i, game in enumerate(game_data):
                game_id = str(game[2])  # GAME_ID
                home_team_id = game[6]  # HOME_TEAM_ID
                visitor_team_id = game[7]  # VISITOR_TEAM_ID
                arena = game[15]  # ARENA_NAME
                
                # Get scores from LineScore (two rows per game: away team then home team)
                home_score = line_score[i*2 + 1][22]  # PTS column for home team
                away_score = line_score[i*2][22]      # PTS column for away team
                
                formatted_game = {
                    'game_id': game_id,
                    'home_team': self.team_dict.get(home_team_id),
                    'away_team': self.team_dict.get(visitor_team_id),
                    'home_score': home_score,
                    'away_score': away_score,
                    'arena': arena,
                    'date': date_str
                }
                
                formatted_games.append(formatted_game)
            
            return formatted_games
            
        except Exception as e:
            print(f"Error in get_games_for_date: {str(e)}")
            print(f"Full error details: {str(e.__class__.__name__)}: {str(e)}")
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

    def get_detailed_stats(self, game_id):
        """Get detailed statistics for a specific game."""
        try:
            # Get detailed box score data
            box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
            box_data = box.get_dict()
            
            # Get all the detailed data
            game_info = box_data['resultSets'][4]['rowSet'][0]  # GameInfo
            team_stats = box_data['resultSets'][1]['rowSet']    # OtherStats
            line_score = box_data['resultSets'][5]['rowSet']    # LineScore
            officials = box_data['resultSets'][2]['rowSet']     # Officials
            
            # Initialize the stats dictionary with base data
            stats = {
                'attendance': game_info[1],
                'duration': game_info[2],
                'officials': ", ".join([f"{off[1]} {off[2]}" for off in officials]),
                
                # Quarter scores
                'home_q1': line_score[1][8],
                'home_q2': line_score[1][9],
                'home_q3': line_score[1][10],
                'home_q4': line_score[1][11],
                'away_q1': line_score[0][8],
                'away_q2': line_score[0][9],
                'away_q3': line_score[0][10],
                'away_q4': line_score[0][11],
                
                # Team stats
                'home_paint_points': team_stats[1][4],
                'away_paint_points': team_stats[0][4],
                'home_second_chance_points': team_stats[1][5],
                'away_second_chance_points': team_stats[0][5],
                'home_fast_break_points': team_stats[1][6],
                'away_fast_break_points': team_stats[0][6],
                'home_largest_lead': team_stats[1][7],
                'away_largest_lead': team_stats[0][7]
            }
            
            # Add overtime periods if they exist
            for ot in range(1, 11):  # Check all possible OT periods
                ot_index = 11 + ot  # OT1 starts at index 12
                home_score = line_score[1][ot_index]
                away_score = line_score[0][ot_index]
                
                if home_score > 0 or away_score > 0:  # If either team scored in this OT
                    stats[f'home_ot{ot}'] = home_score
                    stats[f'away_ot{ot}'] = away_score
            
            return stats
            
        except Exception as e:
            print(f"Error getting detailed stats for game {game_id}: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    client = NBAApiClient()
    
    # Test with a specific date
    test_date = "2025-02-12"
    print(f"\nGetting games for {test_date}:")
    
    try:
        games = client.get_games_for_date(test_date)
        print(f"\nFound {len(games)} games:")
        
        for game in games:
            print(f"\n{game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
            print(f"Arena: {game['arena']}")
            print(f"Game ID: {game['game_id']}")
            
            # Test detailed stats
            print("\nDetailed stats:")
            detailed = client.get_detailed_stats(game['game_id'])
            print(detailed)
            
    except Exception as e:
        print(f"Error: {str(e)}")
