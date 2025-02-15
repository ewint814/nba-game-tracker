import sys
import os
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_nba_api_raw():
    print("\nTesting NBA API")
    
    try:
        # First get all teams to create ID to name mapping
        nba_teams = teams.get_teams()
        team_dict = {team['id']: team['full_name'] for team in nba_teams}
        
        # Try to get games from Feb 10, 2025
        test_date = datetime(2025, 2, 10)
        print(f"\nGames for {test_date.strftime('%Y-%m-%d')}:")
        
        board = scoreboardv2.ScoreboardV2(
            game_date=test_date,
            league_id='00',
            day_offset=0
        )
        
        games = board.get_dict()
        game_data = games['resultSets'][0]['rowSet']
        
        print(f"\nFound {len(game_data)} games:")
        for game in game_data:
            home_team_id = game[6]  # HOME_TEAM_ID
            visitor_team_id = game[7]  # VISITOR_TEAM_ID
            arena = game[15]  # ARENA_NAME
            
            home_name = team_dict.get(home_team_id, f"Team ID: {home_team_id}")
            visitor_name = team_dict.get(visitor_team_id, f"Team ID: {visitor_team_id}")
            
            print(f"\n{visitor_name} @ {home_name}")
            print(f"Arena: {arena}")
                
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_nba_api_raw() 