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
  - Player advanced statistics
  - Team advanced statistics
- Test API section with data verification
- Database preview tool for development
- Development tools for schema updates

## Next Steps

### Immediate Tasks
- [ ] Fix Play-In game logic in database
- [ ] Add Play-In games to database
- [ ] Update game type enum to properly handle Play-In games
- [ ] Add support for legacy games (pre-June 2012):

2. Data Dictionary Creation
   - [ ] PlayerAdvancedStats table
   - [ ] TeamAdvancedStats table
   - [ ] Game table
   - [ ] Photo table
   - [ ] InactivePlayer table
   - [ ] Official table
   - [ ] QuarterScores table
   - [ ] TeamStats table
   - [ ] SeriesStats table
   - [ ] LastMeeting table
   - [ ] VenueInfo table
   - [ ] GameFlow table

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

## NBA API Endpoints to Evaluate

### Completed ✅
- [ ] AllTimeLeadersGrids (Not useful - historical league-wide data)
- [ ] AssistLeaders (Not useful - season-level only)
- [ ] AssistTracker (Not useful - single number only)
- [x] BoxScoreAdvancedV2 (Useful - Added to database, implemented for both players and teams)
- [x] BoxScoreAdvancedV3 (Useful - Implemented and replaced V2)

### To Evaluate 🔄
- [ ] BoxScoreDefensive
- [ ] BoxScoreFourFactors
- [ ] BoxScoreMisc
- [ ] BoxScorePlayerTrack
- [ ] BoxScoreScoringV2
- [ ] BoxScoreSummaryV2
- [ ] BoxScoreTraditional
- [ ] BoxScoreUsage
- [ ] CommonAllPlayers
- [ ] CommonPlayerInfo
- [ ] CommonPlayoffSeries
- [ ] CommonTeamRoster
- [ ] CommonTeamYears
- [ ] CumulativePlayerStats
- [ ] DefenseHub
- [ ] DraftBoard
- [ ] DraftCombineDrill
- [ ] DraftCombineNonStationaryShooting
- [ ] DraftCombinePlayerAnthro
- [ ] DraftCombineSpots
- [ ] DraftCombineStats
- [ ] DraftHistory
- [ ] FranchiseHistory
- [ ] FranchiseLeaders
- [ ] GameRotation
- [ ] GLAlumBoxScoreSimilarityScore
- [ ] HomePageLeaders
- [ ] HomePageV2
- [ ] HustleStatsBoxScore
- [ ] InfographicFanDuelPlayer
- [ ] LeadersTiles
- [ ] LeagueDashLineups
- [ ] LeagueDashOppPtShot
- [ ] LeagueDashPlayerBioStats
- [ ] LeagueDashPlayerClutch
- [ ] LeagueDashPlayerPtShot
- [ ] LeagueDashPlayerShotLocations
- [ ] LeagueDashPlayerStats
- [ ] LeagueDashPtDefend
- [ ] LeagueDashPtStats
- [ ] LeagueDashPtTeamDefend
- [ ] LeagueDashTeamClutch
- [ ] LeagueDashTeamPtShot
- [ ] LeagueDashTeamShotLocations
- [ ] LeagueDashTeamStats
- [ ] LeagueGameFinder
- [ ] LeagueGameLog
- [ ] LeagueHustleStatsPlayer
- [ ] LeagueHustleStatsPlayerLeaders
- [ ] LeagueHustleStatsTeam
- [ ] LeagueHustleStatsTeamLeaders
- [ ] LeagueLeaders
- [ ] LeagueLineupViz
- [ ] LeaguePlayerOnDetails
- [ ] LeagueSeasonMatchups
- [ ] LeagueStandings
- [ ] LeagueStandingsV3
- [ ] PlayByPlay
- [ ] PlayByPlayV2
- [ ] PlayerAwards
- [ ] PlayerCareerByCollege
- [ ] PlayerCareerByCollegeRollup
- [ ] PlayerCareerStats
- [ ] PlayerCompare
- [ ] PlayerDashboardByClutch
- [ ] PlayerDashboardByGameSplits
- [ ] PlayerDashboardByGeneralSplits
- [ ] PlayerDashboardByLastNGames
- [ ] PlayerDashboardByOpponent
- [ ] PlayerDashboardByShootingSplits
- [ ] PlayerDashboardByTeamPerformance
- [ ] PlayerDashboardByYearOverYear
- [ ] PlayerDashPtPass
- [ ] PlayerDashPtReb
- [ ] PlayerDashPtShotDefend
- [ ] PlayerDashPtShots
- [ ] PlayerEstimatedMetrics
- [ ] PlayerFantasyProfile
- [ ] PlayerFantasyProfileBarGraph
- [ ] PlayerGameLog
- [ ] PlayerGameLogs
- [ ] PlayerGameStreakFinder
- [ ] PlayerIndex
- [ ] PlayerProfileV2
- [ ] PlayerVsPlayer
- [ ] PlayoffPicture
- [ ] ScoreboardV2
- [ ] ShotChartDetail
- [ ] ShotChartLineupDetail
- [ ] SynergyPlayTypes
- [ ] TeamAndPlayersVsPlayers
- [ ] TeamDashboardByClutch
- [ ] TeamDashboardByGameSplits
- [ ] TeamDashboardByGeneralSplits
- [ ] TeamDashboardByLastNGames
- [ ] TeamDashboardByOpponent
- [ ] TeamDashboardByShootingSplits
- [ ] TeamDashboardByTeamPerformance
- [ ] TeamDashboardByYearOverYear
- [ ] TeamDashLineups
- [ ] TeamDashPtPass
- [ ] TeamDashPtReb
- [ ] TeamDashPtShots
- [ ] TeamDetails
- [ ] TeamEstimatedMetrics
- [ ] TeamGameLog
- [ ] TeamGameLogs
- [ ] TeamGameSplits
- [ ] TeamGameStreakFinder
- [ ] TeamHistoricalLeaders
- [ ] TeamInfoCommon
- [ ] TeamPlayerDashboard
- [ ] TeamPlayerOnOffDetails
- [ ] TeamPlayerOnOffSummary
- [ ] TeamVsPlayer
- [ ] TeamYearByYearStats
- [ ] VideoDetails
- [ ] VideoEvents
- [ ] VideoStatus
- [ ] WinProbabilityPBP

### Notes
- ✅ = Evaluated and decision made
- 🔄 = To be evaluated
- Will update with notes about usefulness for our database as we evaluate each endpoint