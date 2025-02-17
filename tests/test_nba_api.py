import sys
import os
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2, boxscoresummaryv2
from datetime import datetime
from pprint import pprint

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.nba_api_client import NBAApiClient
from src.utils.game_calculations import calculate_series_stats

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

def test_series_data_structure():
    """Test to examine the season series data structure."""
    print("\nExamining Season Series Data")
    
    try:
        # Test with known game
        game_id = "0022400773"  # The game we were testing with
        
        # Get detailed box score data
        box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
        box_data = box.get_dict()
        
        # Find the SeasonSeries result set
        for result_set in box_data['resultSets']:
            if result_set['name'] == 'SeasonSeries':
                print("\nSeason Series Data Structure:")
                print("=" * 50)
                
                # Print headers with indices
                print("\nHeaders:")
                headers = result_set['headers']
                for i, header in enumerate(headers):
                    print(f"{i}: {header}")
                
                # Print all rows of data
                print("\nAll Series Data Rows:")
                for row in result_set['rowSet']:
                    print("\nRow Data:")
                    for i, value in enumerate(row):
                        print(f"{headers[i]}: {value}")
                
                # Print raw data for debugging
                print("\nRaw Data:")
                pprint(result_set['rowSet'])
                
                break
        else:
            print("No SeasonSeries data found!")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

def test_series_calculation():
    """Test the series calculation logic with different scenarios."""
    print("\nTesting Series Calculations")
    print("=" * 50)
    
    # Test Case 1: Home team wins, updating 2-2 series
    print("\nTest Case 1: Home team wins (2-2 → 1-2)")
    print("-" * 30)
    home_score = 149
    away_score = 148
    postgame_wins = 2
    postgame_losses = 2
    postgame_leader = "Tied"
    home_team = "NYK"
    away_team = "ATL"
    
    result = calculate_series_stats(
        home_score=home_score,
        away_score=away_score,
        postgame_home_wins=postgame_wins,
        postgame_home_losses=postgame_losses,
        postgame_leader=postgame_leader,
        home_team_abbrev=home_team,
        away_team_abbrev=away_team
    )
    
    print(f"Input:")
    print(f"• Scores: {home_team} {home_score} - {away_team} {away_score}")
    print(f"• Post-game series: {postgame_wins}-{postgame_losses} ({postgame_leader})")
    print("\nOutput:")
    print(f"• Pre-game series: {result['pregame_series_record']}")
    print(f"• Pre-game leader: {result['pregame_leader']}")
    
    # Test Case 2: Away team wins, updating 1-1 series
    print("\nTest Case 2: Away team wins (1-1 → 1-0)")
    print("-" * 30)
    home_score = 110
    away_score = 120
    postgame_wins = 1
    postgame_losses = 1
    postgame_leader = "Tied"
    
    result = calculate_series_stats(
        home_score=home_score,
        away_score=away_score,
        postgame_home_wins=postgame_wins,
        postgame_home_losses=postgame_losses,
        postgame_leader=postgame_leader,
        home_team_abbrev=home_team,
        away_team_abbrev=away_team
    )
    
    print(f"Input:")
    print(f"• Scores: {home_team} {home_score} - {away_team} {away_score}")
    print(f"• Post-game series: {postgame_wins}-{postgame_losses} ({postgame_leader})")
    print("\nOutput:")
    print(f"• Pre-game series: {result['pregame_series_record']}")
    print(f"• Pre-game leader: {result['pregame_leader']}")
    
    # Test Case 3: First meeting (0-0)
    print("\nTest Case 3: First meeting")
    print("-" * 30)
    result = calculate_series_stats(
        home_score=100,
        away_score=95,
        postgame_home_wins=1,
        postgame_home_losses=0,
        postgame_leader=home_team,
        home_team_abbrev=home_team,
        away_team_abbrev=away_team
    )
    
    print(f"Input:")
    print(f"• Scores: {home_team} 100 - {away_team} 95")
    print(f"• Post-game series: 1-0 ({home_team})")
    print("\nOutput:")
    print(f"• Pre-game series: {result['pregame_series_record']}")
    print(f"• Pre-game leader: {result['pregame_leader']}")

def test_last_meeting_structure():
    """Test to examine the last meeting data structure."""
    print("\nExamining Last Meeting Data")
    print("=" * 50)
    
    try:
        # Test with known game
        game_id = "0022400773"  # Use the same test game ID
        
        # Get detailed box score data
        box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
        box_data = box.get_dict()
        
        # Find the LastMeeting result set
        for result_set in box_data['resultSets']:
            if result_set['name'] == 'LastMeeting':
                print("\nLast Meeting Data Structure:")
                print("=" * 50)
                
                # Print headers with indices
                print("\nHeaders:")
                headers = result_set['headers']
                for i, header in enumerate(headers):
                    print(f"{i}: {header}")
                
                # Print data with headers
                print("\nData:")
                if result_set['rowSet']:
                    row = result_set['rowSet'][0]
                    for i, value in enumerate(row):
                        print(f"{headers[i]}: {value}")
                else:
                    print("No last meeting data found!")
                
                # Print raw data for debugging
                print("\nRaw Data:")
                pprint(result_set['rowSet'])
                
                break
        else:
            print("No LastMeeting result set found!")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

def test_available_endpoints():
    """List all available NBA API endpoints with their descriptions."""
    from nba_api.stats import endpoints
    import inspect
    
    print("\nNBA API Available Endpoints")
    print("=" * 50)
    
    # Get all endpoint classes from the endpoints module
    endpoint_classes = [obj for name, obj in inspect.getmembers(endpoints) 
                       if inspect.isclass(obj) and obj.__module__.startswith('nba_api.stats.endpoints')]
    
    for endpoint in sorted(endpoint_classes, key=lambda x: x.__name__):
        print(f"\n{endpoint.__name__}")
        print("-" * len(endpoint.__name__))
        
        # Get endpoint description if available
        if endpoint.__doc__:
            print(f"Description: {endpoint.__doc__.strip()}")
        
        # Try to get an example of available parameters
        try:
            params = endpoint.expected_parameters
            if params:
                print("Parameters:")
                for param in params:
                    print(f"  - {param}")
        except AttributeError:
            pass

def test_endpoint_details(endpoint_name="BoxScoreSummaryV2"):
    """Examine a specific NBA API endpoint in detail."""
    from nba_api.stats import endpoints
    import inspect
    
    print(f"\nExamining Endpoint: {endpoint_name}")
    print("=" * 50)
    
    try:
        # Get the endpoint class
        endpoint_class = getattr(endpoints, endpoint_name)
        
        # Print description
        if endpoint_class.__doc__:
            print(f"\nDescription:")
            print(endpoint_class.__doc__.strip())
        
        # Print parameters
        print("\nRequired Parameters:")
        if hasattr(endpoint_class, 'expected_parameters'):
            for param in endpoint_class.expected_parameters:
                print(f"  - {param}")
        
        # Try to make a sample request
        print("\nExample Response Structure:")
        if endpoint_name == "BoxScoreSummaryV2":
            # Use our test game ID
            response = endpoint_class(game_id="0022400773")
        elif endpoint_name == "ScoreboardV2":
            # Use our test date
            response = endpoint_class(game_date=datetime(2025, 2, 10))
        else:
            print("Add test parameters for this endpoint")
            return
            
        data = response.get_dict()
        
        # Print available result sets
        print("\nAvailable Result Sets:")
        for i, result_set in enumerate(data['resultSets']):
            print(f"\n{i}: {result_set['name']}")
            print("Headers:")
            for header in result_set['headers']:
                print(f"  - {header}")
            if result_set['rowSet']:
                print(f"\nExample Row:")
                pprint(result_set['rowSet'][0])
            
    except Exception as e:
        print(f"Error examining endpoint: {str(e)}")

def test_endpoints_in_groups():
    """Examine NBA API endpoints in groups of 3."""
    from nba_api.stats import endpoints
    import inspect
    
    # Get all endpoint classes
    endpoint_classes = [obj for name, obj in inspect.getmembers(endpoints) 
                       if inspect.isclass(obj) and obj.__module__.startswith('nba_api.stats.endpoints')]
    
    # Sort alphabetically
    endpoint_classes.sort(key=lambda x: x.__name__)
    
    # Common parameters we'll use
    SAMPLE_PLAYER_ID = "1628369"  # Jayson Tatum
    SAMPLE_TEAM_ID = "1610612738"  # Celtics
    SAMPLE_GAME_ID = "0022400773"
    SAMPLE_SEASON = "2023-24"
    SAMPLE_DATE = datetime(2025, 2, 10)
    
    # Process next 3 endpoints
    for endpoint_class in endpoint_classes[3:6]:  # BoxScore endpoints
        print("\n")
        print("=" * 100)
        print(f"ENDPOINT: {endpoint_class.__name__}")
        print("=" * 100)
        
        # Print description
        if endpoint_class.__doc__:
            print(f"\nDescription:")
            print(endpoint_class.__doc__.strip())
        
        # Print parameters
        print("\nRequired Parameters:")
        if hasattr(endpoint_class, 'expected_parameters'):
            for param in endpoint_class.expected_parameters:
                print(f"  - {param}")
        
        # Try to make a sample request
        print("\nExample Response Structure:")
        try:
            # Handle different endpoints with appropriate parameters
            if endpoint_class.__name__.startswith("BoxScore"):
                response = endpoint_class(game_id=SAMPLE_GAME_ID)
            elif "player" in endpoint_class.__name__.lower():
                response = endpoint_class(player_id=SAMPLE_PLAYER_ID)
            elif "team" in endpoint_class.__name__.lower():
                response = endpoint_class(team_id=SAMPLE_TEAM_ID)
            elif "game" in endpoint_class.__name__.lower():
                response = endpoint_class(game_id=SAMPLE_GAME_ID)
            elif "season" in endpoint_class.__name__.lower():
                response = endpoint_class(season=SAMPLE_SEASON)
            else:
                print("No sample request configured for this endpoint")
                continue
                
            data = response.get_dict()
            
            # Print available result sets
            print("\nAvailable Result Sets:")
            for i, result_set in enumerate(data['resultSets']):
                print(f"\n{i}: {result_set['name']}")
                print("Headers:")
                for header in result_set['headers']:
                    print(f"  - {header}")
                if result_set['rowSet']:
                    print(f"\nExample Row:")
                    pprint(result_set['rowSet'][0])
                    
        except Exception as e:
            print(f"Error making sample request: {str(e)}")
        
        print("\n" + "-" * 100)  # Separator between endpoints

def test_boxscore_advanced():
    """Test to see all available fields from BoxScoreAdvancedV2."""
    from nba_api.stats import endpoints
    
    # Test with two different game IDs
    game_ids = ["0022400773", "0022300642"]
    
    for game_id in game_ids:
        print(f"\nTesting Game ID: {game_id}")
        print("=" * 50)
        
        response = endpoints.BoxScoreAdvancedV2(game_id=game_id)
        data = response.get_dict()
        
        # Print all headers first
        headers = data['resultSets'][0]['headers']
        print("\nField Names:")
        for i, header in enumerate(headers):
            print(f"{i}: {header}")
            
        # Find TM_TOV_PCT index
        tov_pct_index = headers.index('TM_TOV_PCT')
        print(f"\nTM_TOV_PCT is at index: {tov_pct_index}")
        
        # Show some sample values
        print("\nSample TOV_RATIO values:")
        for row in data['resultSets'][0]['rowSet'][:5]:  # First 5 players
            player_name = row[5]
            tov_pct = row[tov_pct_index]
            print(f"{player_name}: {tov_pct}")

if __name__ == "__main__":
    test_boxscore_advanced() 