# NBA Game Tracker

A personal application to track and analyze NBA games I've attended, built with Python, Streamlit, and the NBA API.

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

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run streamlit/main_app.py
   ```

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