"""
NBA API Client Module

This module provides a wrapper around the nba_api package to fetch game data,
statistics, and other NBA-related information.
"""

from nba_api.stats.endpoints import scoreboardv2, boxscoresummaryv2, boxscoreadvancedv3
from nba_api.stats.static import teams
from datetime import datetime
from src.utils.game_calculations import calculate_series_stats

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
            
            # Get all the detailed data from each result set
            game_summary = box_data['resultSets'][0]['rowSet'][0]    # GameSummary
            team_stats = box_data['resultSets'][1]['rowSet']         # OtherStats
            officials = box_data['resultSets'][2]['rowSet']          # Officials
            inactive_players = box_data['resultSets'][3]['rowSet']   # InactivePlayers
            game_info = box_data['resultSets'][4]['rowSet'][0]       # GameInfo
            line_score = box_data['resultSets'][5]['rowSet']         # LineScore
            last_meeting = box_data['resultSets'][6]['rowSet'][0]    # LastMeeting
            season_series = box_data['resultSets'][7]['rowSet'][0]   # SeasonSeries
            
            # Get team stats
            home_team_stats = next(stats for stats in team_stats if stats[1] == game_summary[6])  # Match home_team_id
            away_team_stats = next(stats for stats in team_stats if stats[1] == game_summary[7])  # Match visitor_team_id
            
            # Initialize the stats dictionary with base data
            stats = {
                # Game Summary Data
                'home_team_id': game_summary[6],
                'visitor_team_id': game_summary[7],
                'season': game_summary[8],
                'national_tv': game_summary[11],
                
                # Game Info
                'attendance': game_info[1],
                'duration': game_info[2],
                
                # Team Stats
                'home_team_abbrev': home_team_stats[2],  # Fixed: Use home team stats
                'away_team_abbrev': away_team_stats[2],  # Fixed: Use away team stats
                'home_paint_points': home_team_stats[4],
                'away_paint_points': away_team_stats[4],
                'home_second_chance_points': home_team_stats[5],
                'away_second_chance_points': away_team_stats[5],
                'home_fast_break_points': home_team_stats[6],
                'away_fast_break_points': away_team_stats[6],
                'home_largest_lead': home_team_stats[7],
                'away_largest_lead': away_team_stats[7],
                'lead_changes': home_team_stats[8],
                'times_tied': home_team_stats[9],
                'home_team_turnovers': home_team_stats[10],
                'away_team_turnovers': away_team_stats[10],
                'home_total_turnovers': home_team_stats[11],
                'away_total_turnovers': away_team_stats[11],
                'home_team_rebounds': home_team_stats[12],
                'away_team_rebounds': away_team_stats[12],
                'home_points_off_to': home_team_stats[13],
                'away_points_off_to': away_team_stats[13],
                
                # Quarter scores
                'home_q1': line_score[1][8],
                'home_q2': line_score[1][9],
                'home_q3': line_score[1][10],
                'home_q4': line_score[1][11],
                'away_q1': line_score[0][8],
                'away_q2': line_score[0][9],
                'away_q3': line_score[0][10],
                'away_q4': line_score[0][11],
                
                # Team Records
                'home_team_wins': int(line_score[1][7].split('-')[0]),
                'home_team_losses': int(line_score[1][7].split('-')[1]),
                'away_team_wins': int(line_score[0][7].split('-')[0]),
                'away_team_losses': int(line_score[0][7].split('-')[1]),
                
                # Officials with complete info
                'officials_complete': [
                    {
                        'id': official[0],
                        'first_name': official[1],
                        'last_name': official[2],
                        'jersey_num': official[3]
                    } for official in officials
                ],
                
                # Keep simple officials string for backward compatibility
                'officials': ", ".join([f"{off[1]} {off[2]}" for off in officials]),
                
                # Inactive Players
                'inactive_players': [
                    {
                        'player_id': player[0],
                        'first_name': player[1],
                        'last_name': player[2],
                        'jersey_num': player[3],
                        'team_id': player[4],
                        'team_city': player[5],
                        'team_name': player[6],
                        'team_abbrev': player[7]
                    } for player in inactive_players
                ],
                
                # Last Meeting
                'last_meeting_game_id': last_meeting[1],
                'last_meeting_game_date': last_meeting[2],
                'last_meeting_home_team_id': last_meeting[3],
                'last_meeting_home_city': last_meeting[4],
                'last_meeting_home_name': last_meeting[5],
                'last_meeting_home_abbrev': last_meeting[6],
                'last_meeting_home_points': last_meeting[7],
                'last_meeting_visitor_team_id': last_meeting[8],
                'last_meeting_visitor_city': last_meeting[9],
                'last_meeting_visitor_name': last_meeting[10],
                'last_meeting_visitor_abbrev': last_meeting[11],
                'last_meeting_visitor_points': last_meeting[12],
            }
            
            # Add overtime periods if they exist
            for ot in range(1, 11):  # Check all possible OT periods
                ot_index = 11 + ot  # OT1 starts at index 12
                home_score = line_score[1][ot_index]
                away_score = line_score[0][ot_index]
                
                if home_score > 0 or away_score > 0:  # If either team scored in this OT
                    stats[f'home_ot{ot}'] = home_score
                    stats[f'away_ot{ot}'] = away_score
            
            # Get post-game series info
            home_wins = season_series[4]
            home_losses = season_series[5]
            series_leader = season_series[6]
            
            # Calculate pre-game series stats
            home_score = line_score[1][22]  # PTS column
            away_score = line_score[0][22]  # PTS column
            
            pregame_stats = calculate_series_stats(
                home_score=home_score,
                away_score=away_score,
                postgame_home_wins=home_wins,
                postgame_home_losses=home_losses,
                postgame_leader=series_leader,
                home_team_abbrev=home_team_stats[2],  # Fixed: Use home team stats
                away_team_abbrev=away_team_stats[2]   # Fixed: Use away team stats
            )
            
            stats.update({
                # Post-game series info
                'home_team_series_wins': home_wins,
                'home_team_series_losses': home_losses,
                'series_leader': series_leader,
                
                # Pre-game series info
                'pregame_home_team_series_wins': pregame_stats['pregame_home_wins'],
                'pregame_home_team_series_losses': pregame_stats['pregame_home_losses'],
                'pregame_series_leader': pregame_stats['pregame_leader'],
                'pregame_series_record': pregame_stats['pregame_series_record']
            })
            
            return stats
            
        except Exception as e:
            print(f"Error getting detailed stats for game {game_id}: {str(e)}")
            raise

    def get_advanced_stats(self, game_id):
        """
        Get advanced statistics for a specific game using V3 endpoint.
        
        Args:
            game_id (str): NBA API game ID
            
        Returns:
            dict: Dictionary containing advanced stats for players and teams
        """
        try:
            response = boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game_id)
            data = response.get_dict()
            box_score = data['boxScoreAdvanced']
            
            # Collect all players from both teams with their team info
            players = []
            for team_type in ['homeTeam', 'awayTeam']:
                if team_type in box_score:
                    team = box_score[team_type]
                    team_info = {
                        'teamId': team['teamId'],
                        'teamCity': team['teamCity'],
                        'teamName': team['teamName'],
                        'teamTricode': team['teamTricode'],
                        'teamSlug': team['teamSlug']
                    }
                    
                    # Add team info to each player
                    if 'players' in team:
                        for player in team['players']:
                            player.update(team_info)
                            players.append(player)
            
            # Collect team stats
            teams = []
            for team_type in ['homeTeam', 'awayTeam']:
                if team_type in box_score:
                    teams.append(box_score[team_type])
            
            return {
                'player_stats': players,
                'team_stats': teams
            }
            
        except Exception as e:
            print(f"Error getting advanced stats for game {game_id}: {str(e)}")
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
