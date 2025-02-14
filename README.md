# Basketball Game Tracker

A personal basketball game tracking application that helps fans document and analyze games they've attended. Track any team, any game, with rich statistics and personal memories.

## Features
- Track games you've attended for any team
- Comprehensive game statistics
- Personal memories and photos
- Seat tracking and ticket information
- Weather and venue metadata
- Historical data and trends
- Exportable reports and visualizations

## Use Cases
- Personal game history tracking
- Season ticket holder management
- Family memory collection
- Arena/section analysis for future ticket purchases
- Statistical analysis of attended games
- Share experiences with other fans

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run the Streamlit app: `streamlit run streamlit/app.py`

## Project Structure

basketball-game-tracker/
├── src/
│   ├── data/
│   │   ├── basketball_reference_scraper.py  # Basketball Reference data scraping
│   │   ├── nba_api_client.py               # NBA API integration
│   │   └── database_models.py              # Database models and schemas
│   ├── core/
│   │   ├── game_tracker.py                 # Core game tracking logic
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
└── docs/                                   # Documentation

## Contributing
We welcome contributions from the basketball community! 