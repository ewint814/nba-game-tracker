import streamlit as st
import importlib.util
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time

def fetch_html_for_date(date):
    formatted_date = datetime.strptime(date, "%Y-%m-%d")
    url = f"https://www.basketball-reference.com/boxscores/?month={formatted_date.month}&day={formatted_date.day}&year={formatted_date.year}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {date}. Status code: {response.status_code}")
    return response.text

def parse_celtics_games(html):
    soup = BeautifulSoup(html, 'html.parser')
    game_summaries = soup.find_all('div', class_='game_summary expanded nohover')
    
    games = []
    
    for game in game_summaries:
        teams_table = game.find('table', class_='teams')
        rows = teams_table.find_all('tr')
        if not rows:
            continue
        
        winner_row = game.find('tr', class_='winner')
        loser_row = game.find('tr', class_='loser')
        
        winner_team = winner_row.find('td').text if winner_row else "Unknown"
        winner_score = int(winner_row.find('td', class_='right').text) if winner_row else 0
        loser_team = loser_row.find('td').text if loser_row else "Unknown"
        loser_score = int(loser_row.find('td', class_='right').text) if loser_row else 0
        
        if "Boston" not in [winner_team, loser_team]:
            continue
        
        box_score_link = game.find('p', class_='links').find('a', href=True)['href']
        box_score_url = f"https://www.basketball-reference.com{box_score_link}"
        
        games.append({
            "Date": None,
            "Winner": winner_team,
            "Winner Score": winner_score,
            "Loser": loser_team,
            "Loser Score": loser_score,
            "Box Score URL": box_score_url
        })
    
    return games

def extract_game_metadata_with_regex(html):
    metadata = {}

    refs_match = re.search(r'Officials:.*?<a.*?</div>', html, re.DOTALL)
    if refs_match:
        refs_html = refs_match.group()
        refs = re.findall(r'<a.*?>(.*?)</a>', refs_html)
        metadata['refs'] = ", ".join(refs)
    else:
        metadata['refs'] = None

    attendance_match = re.search(r'Attendance:.*?</div>', html, re.DOTALL)
    if attendance_match:
        raw_text = attendance_match.group()
        clean_text = re.sub(r'<.*?>', '', raw_text)
        metadata['attendance'] = clean_text.replace("&nbsp;", " ").split(":")[-1].strip()
    else:
        metadata['attendance'] = None

    time_match = re.search(r'Time of Game:.*?</div>', html, re.DOTALL)
    if time_match:
        raw_text = time_match.group()
        clean_text = re.sub(r'<.*?>', '', raw_text)
        metadata['time_of_game'] = clean_text.replace("&nbsp;", " ").split(": ", 1)[-1].strip()
    else:
        metadata['time_of_game'] = None

    return metadata

def parse_inactive_players_section(html):
    """
    Parse the HTML for inactive players and their teams.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Locate the 'Inactive:' keyword with robust matching
    inactive_section = soup.find('strong', string=lambda text: text and "Inactive:" in text.strip())
    if not inactive_section:
        print("Debug: 'Inactive:' section not found.")
        return []  # Return an empty list if not found

    # Extract the parent container for the inactive section
    inactive_html = inactive_section.parent

    inactive_data = []

    # Parse each team and its inactive players
    for team_span in inactive_html.find_all('span'):
        team_abbr = team_span.find('strong').text.strip()  # Extract team abbreviation

        # Collect all player names for this team
        for sibling in team_span.find_next_siblings():
            if sibling.name != 'a':  # Stop parsing when siblings are no longer player links
                break
            player_name = sibling.text.strip()
            inactive_data.append({
                'Player': player_name,
                'Team': team_abbr,
                'reason_basic': 'Inactive',
                'reason_advanced': 'Inactive'
            })

    return inactive_data

def fetch_game_details(url):
    """
    Fetch and parse game details to determine if it's a playoff game
    and extract the round and game number if applicable.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the top section of the page where the date and game info is located
    top_text = soup.text.strip()  # Get the entire page text
    playoff_match = re.search(
        r'(NBA Finals|Conference Finals|First Round|Second Round|Play-In Tournament),?\s*Game (\d+)', 
        top_text, 
        re.IGNORECASE
    )

    if playoff_match:
        round_info = playoff_match.group(1)
        game_number = int(playoff_match.group(2))
        return {
            "is_playoff": True,
            "round": round_info,
            "game_number": game_number
        }
    
    # If no playoff information is found
    return {
        "is_playoff": False,
        "round": None,
        "game_number": None
    }

def parse_team_totals(soup, team_abbr, table_id):
    """
    Extract team totals from the specified table and team.
    """
    table = soup.find('table', id=table_id)
    if not table:
        return {}
    
    tfoot = table.find('tfoot')
    if not tfoot:
        return {}
    
    totals_row = tfoot.find('tr')
    totals = {f"team_total_{stat['data-stat']}": stat.text.strip() for stat in totals_row.find_all('td')}
    totals['Team'] = team_abbr
    return totals

def parse_box_score(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch box score. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    all_team_data = []
    team_totals = []
    
    # Get team abbreviations from line score DataFrame
    line_score_df, _ = parse_line_score_and_four_factors(response.text)

    if line_score_df.empty:
        print("Warning: Line score DataFrame is empty. Cannot proceed.")
        return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames
    
    team_abbrs = line_score_df['Team'].tolist()
    
    print(f"Found teams: {team_abbrs}")  # Debug print

    # Now parse box scores for each team
    for team_abbr in team_abbrs:
        # Dynamically find tables for the current team
        tables = soup.find_all('table', id=lambda x: x and x.startswith(f'box-{team_abbr}-'))
        table_ids = [table.get('id') for table in tables if table.get('id')]
        
        team_dfs = []

        for table_id in table_ids:
            table = soup.find('table', id=table_id)
            if not table:
                continue
            
            table_suffix = table_id.split('-')[-2]
            if table_suffix == "game":
                table_suffix = table_id.split('-')[-1]
            table_suffix = table_suffix.replace("-basic", "")

            rows = table.find('tbody').find_all('tr')
            table_data = []
            for idx, row in enumerate(rows):
                player_cell = row.find('th')
                if not player_cell or 'Reserves' in player_cell.text:
                    continue
                
                player_name = player_cell.text.strip()
                stats = {f"{stat['data-stat']}_{table_suffix}": stat.text.strip() for stat in row.find_all('td')}
                stats['Player'] = player_name
                stats['Team'] = team_abbr

                # Assign roles
                if table_suffix == 'basic':
                    if stats.get("reason_basic") == "Did Not Dress":
                        stats['role'] = "Inactive"
                    else:
                        stats['role'] = 'Starter' if idx < 5 else 'Reserve'
                
                table_data.append(stats)
            
            table_df = pd.DataFrame(table_data)
            if not table_df.empty:
                team_dfs.append(table_df)

            # Extract team totals
            totals = parse_team_totals(soup, team_abbr, table_id)
            if totals:
                team_totals.append(totals)

        if team_dfs:
            team_merged_df = team_dfs[0]
            for other_df in team_dfs[1:]:
                team_merged_df = pd.merge(
                    team_merged_df, other_df, on=['Player', 'Team'], how='outer'
                )
            all_team_data.append(team_merged_df)

    final_df = pd.concat(all_team_data, ignore_index=True) if all_team_data else pd.DataFrame()

    # Add team totals
    team_totals_df = pd.DataFrame(team_totals)
    
    return final_df, team_totals_df

def parse_line_score_and_four_factors(html):
    """
    Parse the line score and four factors tables from the box score HTML, dynamically handling overtime columns.
    """
    line_score_data = []
    four_factors_data = []

    # Extract line score table
    soup = BeautifulSoup(html, 'html.parser')
    line_score_table = soup.find('table', id='line_score')
    if not line_score_table:
        line_score_match = re.search(r'<table[^>]*id="line_score".*?</table>', html, re.DOTALL)
        if line_score_match:
            line_score_html = line_score_match.group()
            line_score_table = BeautifulSoup(line_score_html, 'html.parser')

    overtime_info = None  # Initialize overtime information
    if line_score_table:
        # Extract column headers dynamically (e.g., q1, q2, q3, q4, ot1, ot2, ...)
        header_row = line_score_table.find('thead').find_all('th')
        column_names = ["Team"]  # Initialize with "Team"
        for th in header_row:
            col_name = th.text.strip().lower()
            # Include only valid scoring columns (e.g., q1, q2, ..., ot1, ot2, total)
            if col_name.isdigit() or "ot" in col_name or col_name == "t":
                column_names.append(col_name)

        # Check for overtime columns
        extra_columns = len(column_names) - 6  # Subtract standard 6 columns (Team + 4 quarters + Total)
        if extra_columns > 0:
            overtime_info = f"{extra_columns}OT" if extra_columns > 1 else "OT"
        
        rows = line_score_table.find('tbody').find_all('tr')
        for row in rows:
            team_name = row.find('th').text.strip()
            team_data = [td.text.strip() for td in row.find_all('td')]
            if team_name:
                # Create a dictionary dynamically based on columns
                row_data = {"Team": team_name}
                for col_name, col_value in zip(column_names[1:], team_data):
                    row_data[col_name] = col_value
                # Add overtime information to each row
                if overtime_info:
                    row_data["overtime_info"] = overtime_info
                else:
                    row_data["overtime_info"] = "No OT"
                line_score_data.append(row_data)

    # Extract four factors table
    four_factors_table = soup.find('table', id='four_factors')
    if not four_factors_table:
        four_factors_match = re.search(r'<table[^>]*id="four_factors".*?</table>', html, re.DOTALL)
        if four_factors_match:
            four_factors_html = four_factors_match.group()
            four_factors_table = BeautifulSoup(four_factors_html, 'html.parser')

    if four_factors_table:
        rows = four_factors_table.find('tbody').find_all('tr')
        for row in rows:
            team_name = row.find('th').text.strip()
            factors = [td.text.strip() for td in row.find_all('td')]
            if team_name and len(factors) >= 4:
                four_factors_data.append({
                    "Team": team_name,
                    "efg_pct": factors[0],
                    "tov_pct": factors[1],
                    "orb_pct": factors[2],
                    "ft_rate": factors[3]
                })

    # Create DataFrames
    line_score_df = pd.DataFrame(line_score_data)
    four_factors_df = pd.DataFrame(four_factors_data)

    # Add descriptive column names
    if not line_score_df.empty:
        line_score_df = line_score_df.rename(columns=lambda col: f"line_score_{col}" if col != "Team" else col)

    if not four_factors_df.empty:
        four_factors_df = four_factors_df.rename(columns=lambda col: f"four_factors_{col}" if col != "Team" else col)

    return line_score_df, four_factors_df

def parse_box_score_with_inactives_and_team_stats(url):
    """
    Parse the box score URL to extract player stats, assign roles, team stats, and metadata.
    """
    # Parse player stats with roles
    stats_df, team_totals_df = parse_box_score(url)

    # Fetch the HTML content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch box score. Status code: {response.status_code}")
    
    # Parse line score and four factors
    line_score_df, four_factors_df = parse_line_score_and_four_factors(response.text)

    # Fetch playoff details and add to team_totals_df
    playoff_details = fetch_game_details(url)
    if "playoff_info" not in team_totals_df.columns:
        playoff_info = (
            f"{playoff_details['round']} Game {playoff_details['game_number']}"
            if playoff_details["is_playoff"]
            else "Regular Season"
        )
        team_totals_df["playoff_info"] = playoff_info

    # Extract inactive players
    inactive_players = parse_inactive_players_section(response.text)
    inactive_df = pd.DataFrame(inactive_players)

    # Add missing columns to inactive players DataFrame
    if not inactive_df.empty:
        missing_columns = {col: pd.NA for col in stats_df.columns if col not in inactive_df.columns}
        inactive_df = pd.concat([inactive_df, pd.DataFrame(missing_columns, index=inactive_df.index)], axis=1)
        inactive_df["role"] = "Inactive"

    # Combine stats and inactive players
    full_data = pd.concat([stats_df, inactive_df], ignore_index=True)

    # Extract metadata
    metadata = extract_game_metadata_with_regex(response.text)

    # Separate active and inactive players
    active_players = full_data[full_data["role"] != "Inactive"].copy()
    inactive_players = full_data[full_data["role"] == "Inactive"].copy()

    # Add metadata only to active players
    if metadata:
        metadata_df = pd.DataFrame([metadata] * len(active_players), columns=metadata.keys())
        active_players = pd.concat([active_players.reset_index(drop=True), metadata_df.reset_index(drop=True)], axis=1)

    # Assign NaN values for metadata columns to inactive players
    if metadata:
        for key in metadata.keys():
            inactive_players[key] = pd.NA

    # Combine active and inactive players back together
    full_data = pd.concat([active_players, inactive_players], ignore_index=True)

    return full_data, line_score_df, four_factors_df, team_totals_df


def merge_team_stats(player_stats_df, line_score_df, four_factors_df, team_totals_df):
    """
    Merge team-level stats with player stats, avoiding duplications.
    """
    
    # Standardize team names once
    for df in [player_stats_df, line_score_df, four_factors_df, team_totals_df]:
        if not df.empty:
            df["Team"] = df["Team"].str.strip().str.upper()
    
        # Define active players as those with NaN in 'reason_basic'
    active_players = player_stats_df[player_stats_df['reason_basic'].isna()].copy()
    inactive_players = player_stats_df[player_stats_df['reason_basic'].notna()].copy()
    
    print(f"Active players: {len(active_players)}, Inactive players: {len(inactive_players)}")
    
    # First, consolidate team totals to one row per team
    if not team_totals_df.empty:
        # Group by Team and take the first row of each group
        team_totals_df = team_totals_df.groupby('Team').first().reset_index()
        print(f"Consolidated team totals shape: {team_totals_df.shape}")
    
    # Merge team stats only for active players
    if not team_totals_df.empty:
        # Remove any existing team_total columns from active_players
        existing_total_cols = [col for col in active_players.columns if col.startswith('team_total_')]
        if existing_total_cols:
            active_players = active_players.drop(columns=existing_total_cols)
        
        active_players = pd.merge(active_players, team_totals_df, on="Team", how="left")
    
    if not line_score_df.empty:
        existing_ls_cols = [col for col in active_players.columns if col.startswith('line_score_')]
        if existing_ls_cols:
            active_players = active_players.drop(columns=existing_ls_cols)
            
        line_score_cols = {col: col if col == 'Team' or col.startswith('line_score_') 
                          else f'line_score_{col}' for col in line_score_df.columns}
        line_score_df = line_score_df.rename(columns=line_score_cols)
        
        active_players = pd.merge(active_players, line_score_df, on="Team", how="left")
    
    if not four_factors_df.empty:
        existing_ff_cols = [col for col in active_players.columns if col.startswith('four_factors_')]
        if existing_ff_cols:
            active_players = active_players.drop(columns=existing_ff_cols)
            
        four_factors_cols = {col: col if col == 'Team' or col.startswith('four_factors_') 
                           else f'four_factors_{col}' for col in four_factors_df.columns}
        four_factors_df = four_factors_df.rename(columns=four_factors_cols)
        
        active_players = pd.merge(active_players, four_factors_df, on="Team", how="left")
    
    # Add NaN values for team stats columns to inactive players
    team_stats_cols = [col for col in active_players.columns 
                      if any(col.startswith(prefix) for prefix in 
                            ['team_total_', 'line_score_', 'four_factors_'])]
    
    for col in team_stats_cols:
        if col not in inactive_players.columns:
            inactive_players[col] = pd.NA
    
    # Combine active and inactive players
    final_df = pd.concat([active_players, inactive_players], ignore_index=True)
    
    print(f"Final shape: {final_df.shape}")
    return final_df

@st.cache_resource
def get_celtics_games_and_stats(date):
    """
    Fetch Celtics games and detailed stats for the given date.
    """
    html = fetch_html_for_date(date)
    celtics_games = parse_celtics_games(html)
    
    all_stats = []
    for game in celtics_games:
        time.sleep(10)  # Add a delay between requests (adjust as needed)
        final_df, line_score_df, four_factors_df, team_totals_df = parse_box_score_with_inactives_and_team_stats(
            game['Box Score URL']
        )
        merged_stats = merge_team_stats(final_df, line_score_df, four_factors_df, team_totals_df)
        all_stats.append(merged_stats)
    
    return pd.concat(all_stats, ignore_index=True)

def determine_year_range(date):
    """
    Determine the NBA season year range based on the date.
    """
    if date.month >= 10:  # October, November, December
        start_year = date.year
        end_year = date.year + 1
    elif date.month <= 6:  # January through June
        start_year = date.year - 1
        end_year = date.year
    else:  # July, August, September
        start_year = date.year
        end_year = date.year + 1
    return f"{start_year}-{end_year}"

def process_dates(dates):
    """
    Process multiple dates to fetch and prepare Celtics game stats.
    """
    all_stats = []
    for date in dates:
        celtics_stats_df = get_celtics_games_and_stats(date)
        
        # Drop unused columns
        columns_to_drop = ['reason_advanced', 'Stat Type_advanced', 'mp_advanced', 'Stat Type_basic', 
                           'reason_q1', 'reason_q2', 'reason_q3', 'reason_q4', 'reason_h1', 'reason_h2']
        df = celtics_stats_df.drop(columns=columns_to_drop, errors='ignore')

        # Rename columns
        df = df.rename(columns={
            'mp_basic': 'mp',
            'reason_basic': 'reason_for_DNP',
            'line_score_t': 'line_score_total'
        })

        # Add the current date as a column
        df['Date'] = pd.to_datetime(date)

        # Add a Year Range column
        df['Year'] = df['Date'].apply(determine_year_range)
        
        # Process game results
        if 'line_score_total' in df.columns:
            game_results = df.groupby('Team')['line_score_total'].sum().reset_index()
            max_score = game_results['line_score_total'].max()
            game_results['game_result'] = game_results['line_score_total'].apply(
                lambda score: 'Loss' if score == max_score else 'Win'
            )
            df = df.merge(game_results[['Team', 'game_result']], on='Team', how='left')

        all_stats.append(df)
    
    return pd.concat(all_stats, ignore_index=True)

# Streamlit App
def main():
    st.title("Celtics Game Stats Analyzer")
    
    # Sidebar: Select Method to Input Dates
    st.sidebar.header("Select Input Method")
    input_method = st.sidebar.radio("Choose how to input dates:", ["Manual Input", "Upload .py File"])
    
    # Manual Input for Dates
    if input_method == "Manual Input":
        dates_input = st.sidebar.text_area(
            "Enter game dates (comma-separated, format YYYY-MM-DD):",
            placeholder="e.g., 2024-11-25, 2024-11-22"
        )
        if dates_input:
            dates = [date.strip() for date in dates_input.split(",")]

            if st.sidebar.button("Fetch Stats"):
                fetch_and_display_stats(dates)

    # Upload .py File with Dates
    elif input_method == "Upload .py File":
        uploaded_file = st.sidebar.file_uploader("Upload a .py file with dates", type=["py"])
        if uploaded_file:
            try:
                # Dynamically load the Python file
                file_path = f"./temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                spec = importlib.util.spec_from_file_location("uploaded_module", file_path)
                uploaded_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(uploaded_module)

                # Check if the uploaded module contains a `dates` list
                if hasattr(uploaded_module, "dates"):
                    dates = uploaded_module.dates
                    st.success(f"Successfully loaded dates: {dates}")
                    
                    if st.sidebar.button("Fetch Stats"):
                        fetch_and_display_stats(dates)
                else:
                    st.error("The uploaded file does not contain a `dates` list.")
            except Exception as e:
                st.error(f"Error processing the uploaded file: {e}")

# Helper Function to Fetch and Display Stats
def fetch_and_display_stats(dates):
    try:
        st.info("Fetching game stats, this may take a moment...")
        combined_df = process_dates(dates)
        
        st.success("Data fetched successfully!")
        st.header("Game Stats")
        st.dataframe(combined_df)
        
        # Option to download the processed data
        csv = combined_df.to_csv(index=False)
        st.download_button("Download Combined Data", csv, "celtics_game_stats.csv", "text/csv")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()