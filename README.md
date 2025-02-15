# NBA Game Tracker

A personal basketball game tracking application that helps fans document and analyze games they've attended. Track any team, any game, with rich statistics and personal memories.

## Features

### Game Recording
- Save any NBA games attended with detailed information:
  - Basic game data (teams, scores, date)
  - Seat location details
  - Personal notes
  - Attendance details

### Game Statistics
- Comprehensive game stats from NBA API:
  - Quarter-by-quarter scoring
  - Paint points
  - Second chance points
  - Fast break points
  - Team largest leads
  - Game attendance
  - Game duration
  - Officials

### Interface
- **Add Game**: Find and save games you've attended
- **My Games**: View your game history
- **Statistics**: Analyze your attendance patterns
- **Test API**: Verify NBA data retrieval

## Project Structure

basketball-game-tracker/
├── src/
│   ├── data/
│   │   ├── basketball_reference_scraper.py  # Basketball Reference data scraping
│   │   ├── nba_api_client.py               # NBA API integration
│   │   └── database_models.py              # Database models and schemas
│   ├── core/
│   │   ├── team_manager.py                 # Team management functionality
│   │   ├── venue_manager.py                # Arena/venue management
│   │   └── user_profile.py                 # User profile handling
│   ├── utils/
│   │   ├── data_validators.py              # Input validation utilities
│   │   └── date_helpers.py                 # Date manipulation helpers
│   └── visualization/
│       ├── game_charts.py                  # Game-specific visualizations
│       └── stat_plots.py                   # Statistical analysis plots
├── streamlit/
│   ├── main_app.py                         # Main Streamlit application
│   └── pages/
│       ├── add_new_game.py                 # Add new game interface
│       ├── view_statistics.py              # Statistics viewing page
│       ├── game_memories.py                # Game memories and photos
│       └── user_settings.py                # User settings page
├── tests/                                  # Test files
│   ├── test_nba_api.py              # NBA API client tests
│   └── test_database.py            # Database models tests
└── docs/                                   # Documentation
└── requirements.txt
└── README.md
└── .gitignore
└── TODO.md




## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run the Streamlit app: `streamlit run streamlit/app.py`

## Usage

### Adding Games
1. Select game date
2. Choose from available games
3. Add your seat and attendance details
4. Save to your collection

### Testing
- Use the Test API section to:
  - Verify NBA API data
  - Check database storage
  - View detailed game stats 