# Basketball Game Tracker TODO

## Completed ✅
- Basic project structure
- Database setup with SQLAlchemy
- NBA API integration for getting game data
- Basic Streamlit interface
- Game saving functionality
- Detailed game stats:
  - Quarter scores and overtime periods
  - Team performance metrics
  - Game flow statistics
  - Officials and inactive players
  - Season series tracking (pre and post-game)
- Test API section with data verification
- Database preview tool for development
- Development tools for schema updates

## Next Steps

### Game Statistics
1. Advanced Statistics
   - [ ] Calculate win/loss records:
     - Overall record when attending
     - Record by team
     - Record by seat location
   - [ ] Series tracking:
     - Season series progression
     - Head-to-head records
   - [ ] Streak tracking:
     - Winning/losing streaks
     - Home/away streaks

2. Data Analysis
   - [ ] Points differential analysis
   - [ ] Close games vs blowouts
   - [ ] Overtime game statistics
   - [ ] Lead changes and comebacks

### Streamlit Interface
1. My Games Page Improvements
   - [ ] Add grouping options:
     - By season/year
     - By team
     - By arena
     - By who attended with
   
   - [ ] Add filtering options:
     - Home/away team filters
     - Date range selector
     - Score filters (close games, blowouts)
     - Arena filter
   
   - [ ] Improve game display:
     - Better score display format
     - Add team logos/colors
     - Show more game stats
     - Better layout for attendance details

2. Statistics Page
   - [ ] Add win/loss record when attending
   - [ ] Calculate points scored/allowed
   - [ ] Track favorite/most opponents seen
   - [ ] Show best/worst games attended

### Development
- [ ] Implement proper database migrations for schema changes
- [ ] Add comprehensive error handling
- [ ] Improve code documentation
- [ ] Add unit tests for game calculations
- [ ] Optimize database queries
- [ ] Add player_ids to inactive players table (requires additional NBA API integration)

### Future Features
- [ ] Add photo gallery
- [ ] Add game highlights/recap links
- [ ] Add memorable moments tracking
- [ ] Add search functionality
- [ ] Add ticket price tracking
- Add data visualization for game statistics
- Add weather data for game days
- Add player stats tracking