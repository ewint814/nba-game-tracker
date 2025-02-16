import sys
import os
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2, boxscoresummaryv2
from datetime import datetime
from pprint import pprint

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.nba_api_client import NBAApiClient

def test_nba_api_raw():
    """Test basic NBA API functionality."""
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

def test_overtime_structure():
    """Test to examine the structure of overtime data in the NBA API."""
    print("\nTesting Overtime Game Structure")
    
    try:
        # Test with known overtime game
        game_id = "0022400773"
        
        # Get detailed box score data
        box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
        box_data = box.get_dict()
        
        # Print all available result sets
        print("\nAvailable Result Sets:")
        for i, result_set in enumerate(box_data['resultSets']):
            print(f"\nResult Set {i}: {result_set['name']}")
            print("Headers:")
            for j, header in enumerate(result_set['headers']):
                print(f"{j}: {header}")
            if result_set['rowSet']:
                print("\nFirst row data:")
                pprint(result_set['rowSet'][0])
            
    except Exception as e:
        print(f"\nError: {str(e)}")

def test_all_stats_structure():
    """Test to examine all available stats in each result set."""
    print("\nExamining All Available Stats")
    
    try:
        # Test with known game
        game_id = "0022400773"
        
        # Get detailed box score data
        box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
        box_data = box.get_dict()
        
        # Print all available result sets with detailed structure
        for i, result_set in enumerate(box_data['resultSets']):
            print(f"\n{'='*50}")
            print(f"Result Set {i}: {result_set['name']}")
            print(f"{'='*50}")
            
            # Print headers with indices
            print("\nHeaders:")
            headers = result_set['headers']
            for j, header in enumerate(headers):
                print(f"{j}: {header}")
            
            # Print first row of data with header labels
            if result_set['rowSet']:
                print("\nFirst Row Data:")
                row = result_set['rowSet'][0]
                for j, value in enumerate(row):
                    print(f"{headers[j]}: {value}")
            else:
                print("\nNo data in this result set")
            
            # Print number of rows
            print(f"\nTotal rows in this set: {len(result_set['rowSet'])}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    # test_nba_api_raw()
    # test_overtime_structure()
    test_all_stats_structure() 