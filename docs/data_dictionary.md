# Data Dictionary

## Game Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | NBA API game identifier |
| date | Date | Game date |
| season | String(7) | Season in YYYY-YY format |
| home_team | String(50) | Home team name |
| away_team | String(50) | Home team name |
| home_team_id | Integer | NBA API home team ID |
| away_team_id | Integer | NBA API away team ID |
| home_team_abbrev | String(3) | Home team abbreviation |
| away_team_abbrev | String(3) | Away team abbreviation |
| home_score | Integer | Home team final score |
| away_score | Integer | Away team final score |
| seat_section | String(20) | Seat section identifier |
| seat_row | String(10) | Seat row identifier |
| seat_number | String(10) | Seat number |
| attended_with | String(200) | Who attended the game with |
| notes | Text | Personal notes about the game |

## Photo Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | Integer | Foreign key to games table |
| file_path | String(500) | Path to stored image file |
| caption | Text | Optional photo description |

## InactivePlayer Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| first_name | String(50) | Player's first name |
| last_name | String(50) | Player's last name |
| jersey_num | Integer | Player's jersey number |
| team_id | Integer | NBA API team identifier |

## Official Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| official_id | Integer | NBA API official identifier |
| name | String(100) | Official's full name |
| jersey_num | Integer | Official's jersey number |

## QuarterScores Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| period | String(3) | Period identifier (Q1, Q2, Q3, Q4, OT1, etc.) |
| home_team_id | Integer | NBA API home team identifier |
| away_team_id | Integer | NBA API away team identifier |
| home_score | Integer | Home team score for the period |
| away_score | Integer | Away team score for the period |

## TeamStats Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| team_id | Integer | NBA API team identifier |
| paint_points | Integer | Points scored in the paint |
| second_chance_points | Integer | Points from second chance opportunities |
| fast_break_points | Integer | Points from fast breaks |
| team_turnovers | Integer | Team turnovers |
| total_turnovers | Integer | Total turnovers (team + individual) |
| team_rebounds | Integer | Team rebounds |
| points_off_to | Integer | Points scored off turnovers |

## SeriesStats Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| pregame_home_team_series_wins | Integer | Home team series wins before game |
| pregame_home_team_series_losses | Integer | Home team series losses before game |
| pregame_series_leader | String(3) | Team abbreviation of series leader before game |
| pregame_series_record | String(10) | Series record before game (e.g., "2-1") |
| postgame_home_team_series_wins | Integer | Home team series wins after game |
| postgame_home_team_series_losses | Integer | Home team series losses after game |
| postgame_series_leader | String(3) | Team abbreviation of series leader after game |
| postgame_series_record | String(10) | Series record after game |

## LastMeeting Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| last_meeting_game_id | String | NBA API game ID of last meeting |
| last_meeting_game_date | Date | Date of last meeting |
| home_team_id | Integer | NBA API home team identifier |
| away_team_id | Integer | NBA API away team identifier |
| home_team_score | Integer | Home team score in last meeting |
| away_team_score | Integer | Away team score in last meeting |

## VenueInfo Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| arena | String(100) | Arena name |
| attendance | Integer | Game attendance |
| duration_minutes | Integer | Game duration in minutes |
| national_tv | String(20) | National TV broadcaster (or 'Local') |

## GameFlow Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| home_largest_lead | Integer | Largest lead by home team |
| away_largest_lead | Integer | Largest lead by away team |
| lead_changes | Integer | Number of lead changes |
| times_tied | Integer | Number of times score was tied |

## PlayerAdvancedStats Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| team_id | Integer | NBA API team identifier |
| player_id | Integer | NBA API player identifier |
| first_name | String(50) | Player's first name |
| last_name | String(50) | Player's last name |
| starting_position | String(5) | Starting position (F, G, C) |
| starter | Boolean | Whether player started the game |
| status | String(20) | Player status |
| status_reason | String(50) | Reason for status if not active |
| minutes | String(8) | Minutes played |
| estimated_offensive_rating | Float | Estimated offensive rating |
| offensive_rating | Float | Actual offensive rating |
| estimated_defensive_rating | Float | Estimated defensive rating |
| defensive_rating | Float | Actual defensive rating |
| estimated_net_rating | Float | Estimated net rating |
| net_rating | Float | Actual net rating |
| assist_percentage | Float | Percentage of team field goals assisted |
| assist_to_turnover | Float | Assist to turnover ratio |
| assist_ratio | Float | Assist ratio |
| offensive_rebound_percentage | Float | Offensive rebound percentage |
| defensive_rebound_percentage | Float | Defensive rebound percentage |
| rebound_percentage | Float | Overall rebound percentage |
| turnover_ratio | Float | Turnover ratio |
| effective_field_goal_percentage | Float | Effective field goal percentage |
| true_shooting_percentage | Float | True shooting percentage |
| usage_percentage | Float | Usage percentage |
| estimated_usage_percentage | Float | Estimated usage percentage |
| estimated_pace | Float | Estimated pace |
| pace | Float | Actual pace |
| pace_per40 | Float | Pace per 40 minutes |
| possessions | Integer | Number of possessions |
| pie | Float | Player Impact Estimate |

## TeamAdvancedStats Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| game_id | String(20) | Foreign key to games table |
| team_id | Integer | NBA API team identifier |
| estimated_offensive_rating | Float | Estimated offensive rating |
| offensive_rating | Float | Actual offensive rating |
| estimated_defensive_rating | Float | Estimated defensive rating |
| defensive_rating | Float | Actual defensive rating |
| estimated_net_rating | Float | Estimated net rating |
| net_rating | Float | Actual net rating |
| assist_percentage | Float | Percentage of team field goals assisted |
| assist_to_turnover | Float | Assist to turnover ratio |
| assist_ratio | Float | Assist ratio |
| offensive_rebound_percentage | Float | Offensive rebound percentage |
| defensive_rebound_percentage | Float | Defensive rebound percentage |
| rebound_percentage | Float | Overall rebound percentage |
| estimated_team_turnover_percentage | Float | Estimated team turnover percentage |
| turnover_ratio | Float | Turnover ratio |
| effective_field_goal_percentage | Float | Effective field goal percentage |
| true_shooting_percentage | Float | True shooting percentage |
| estimated_pace | Float | Estimated pace |
| pace | Float | Actual pace |
| pace_per40 | Float | Pace per 40 minutes |
| possessions | Integer | Number of possessions |
| pie | Float | Player Impact Estimate |