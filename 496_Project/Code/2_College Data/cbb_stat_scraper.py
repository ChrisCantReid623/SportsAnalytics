import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random

# Function to search for a player's profile link on the corresponding alphabet page
def search_player_profile(soup, first_name, last_name):
    first_name = first_name.lower().replace('.', '').strip()
    last_name = last_name.lower().replace('.', '').strip()

    for link in soup.find_all('a'):
        href = link.get('href', '').lower()
        text = link.get_text().lower().replace('.', '').strip()

        if (last_name in href and first_name in href) or (last_name in text and first_name in text):
            profile_url = f"https://www.sports-reference.com{link.get('href')}"
            print(f"\033[92mFound profile for {first_name.capitalize()} {last_name.capitalize()}: {profile_url}\033[0m")
            return profile_url

    print(f"\033[91mProfile for {first_name.capitalize()} {last_name.capitalize()} not found.\033[0m")
    return None

# Function to count the number of seasons played by a player
def extract_position_and_seasons(soup):
    players_per_game_div = soup.find('div', id='all_players_per_game')

    if not players_per_game_div:
        print("Player stats div not found.")
        return "Unknown", 0

    rows = players_per_game_div.find_all('tr', id=lambda value: value and value.startswith("players_per_game.") and "Career" not in value and "conf" not in value)

    if not rows:
        print("No rows found for player stats.")
        return "Unknown", 0

    position = rows[0].find('td', {'data-stat': 'pos'}).get_text() if rows[0].find('td', {'data-stat': 'pos'}) else "Unknown"
    seasons_played = len(rows)

    return position, seasons_played

# Function to extract career stats and handle the absence of 3P% column
def extract_career_stats(soup):
    table = soup.find('table', id='players_per_game')

    if table is None:
        print("Per-game stats table not found.")
        return None

    headers = [th.get('data-stat') for th in table.find('thead').find_all('th')]
    has_3p_pct = 'fg3_pct' in headers

    career_row = table.find('tr', id='players_per_game.Career')

    if not career_row:
        print("Career row not found in the table.")
        return None

    career_stats = [td.get_text() for td in career_row.find_all('td')]

    # If the table does not include 3P%, insert NaN after the 3PA column
    if not has_3p_pct:
        career_stats.insert(9, 'NaN')

    # Remove empty or missing values by filtering out empty strings
    career_stats = [stat if stat.strip() != '' else 'N/A' for stat in career_stats]

    return career_stats

# Function to save player data to a CSV file
def save_player_data(player_name, seasons_played, position, career_stats, output_csv, first_player=False):
    # Set a default value for position if it's missing
    if position.strip() == "":
        position = "Unknown"

    # Remove any 'N/A' values from the player's extracted data to avoid empty spaces
    player_data = [player_name, seasons_played, position] + [stat for stat in career_stats if stat != 'N/A']

    if first_player:
        # Headers with no redundant 'Pos' column
        headers = ['Player', 'Seasons Played', 'Position', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%',
                   '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV',
                   'PF', 'PTS']
        with open(output_csv, 'w') as f:
            pd.DataFrame([headers]).to_csv(f, header=False, index=False)

    with open(output_csv, 'a') as f:
        df = pd.DataFrame([player_data])
        df.to_csv(f, header=False, index=False)

# Function to check if a player has already been processed
def is_player_processed(player_name, processed_players_csv):
    if os.path.exists(processed_players_csv):
        df = pd.read_csv(processed_players_csv)
        # Ensure the file has the 'Player' column, otherwise create it with headers
        if 'Player' not in df.columns:
            df = pd.DataFrame(columns=['Player'])
            df.to_csv(processed_players_csv, index=False)
        return player_name in df['Player'].values
    return False

# Function to mark a player as processed by saving their name
def mark_player_processed(player_name, processed_players_csv):
    if not os.path.exists(processed_players_csv):
        # Create the file with a header if it doesn't exist
        pd.DataFrame(columns=['Player']).to_csv(processed_players_csv, index=False)

    # Append the processed player's name
    with open(processed_players_csv, 'a') as f:
        pd.DataFrame([[player_name]], columns=['Player']).to_csv(f, header=False, index=False)

# Main function to read the CSV and search for player profiles
def main():
    input_csv = "player_names_sorted.csv"
    output_csv = "player_stats.csv"
    processed_players_csv = "processed_players.csv"

    if not os.path.exists(input_csv):
        print(f"Error: The input CSV file '{input_csv}' was not found.")
        return

    df = pd.read_csv(input_csv)

    first_player = True if not os.path.exists(output_csv) else False
    current_letter = ''

    for index, row in df.iterrows():
        first_name = row['First Name']
        last_name = row['Last Name']
        player_name = f"{first_name} {last_name}"

        # Special case for Larry Nance
        if player_name == "Larry Nance":
            profile_url = "https://www.sports-reference.com/cbb/players/larry-nance-2.html"
            print(f"\033[92mFound special case for Larry Nance: {profile_url}\033[0m")

            profile_response = requests.get(profile_url)
            if profile_response.status_code == 200:
                profile_soup = BeautifulSoup(profile_response.content, 'html.parser')

                position, seasons_played = extract_position_and_seasons(profile_soup)
                career_stats = extract_career_stats(profile_soup)

                if career_stats is not None:
                    save_player_data(player_name, seasons_played, position, career_stats, output_csv, first_player)
                    mark_player_processed(player_name, processed_players_csv)
                    first_player = False
                else:
                    print(f"Could not extract career stats for Larry Nance.")
            else:
                print(f"Failed to retrieve profile page for Larry Nance. Status code: {profile_response.status_code}")
            continue  # Skip the rest of the loop for Larry Nance

        if is_player_processed(player_name, processed_players_csv):
            print(f"Skipping {player_name}, already processed.")
            continue

        first_letter = last_name[0].lower()

        if first_letter != current_letter:
            url = f"https://www.sports-reference.com/cbb/players/{first_letter}-index.html"
            response = requests.get(url)

            if response.status_code == 200:
                print(f"Successfully navigated to {url}")
                soup = BeautifulSoup(response.content, 'html.parser')
                current_letter = first_letter
            else:
                print(f"Failed to navigate to {url}. Status code: {response.status_code}")
                continue

        profile_url = search_player_profile(soup, first_name, last_name)

        if profile_url:
            profile_response = requests.get(profile_url)
            if profile_response.status_code == 200:
                profile_soup = BeautifulSoup(profile_response.content, 'html.parser')

                position, seasons_played = extract_position_and_seasons(profile_soup)
                career_stats = extract_career_stats(profile_soup)

                if career_stats is not None:
                    save_player_data(player_name, seasons_played, position, career_stats, output_csv, first_player)
                    mark_player_processed(player_name, processed_players_csv)
                    first_player = False
                else:
                    print(f"Could not extract career stats for {first_name} {last_name}")
            else:
                print(f"Failed to retrieve profile page for {first_name} {last_name}. Status code: {profile_response.status_code}")
        else:
            print(f"\033[91mProfile for {first_name} {last_name} not found.\033[0m")

        time.sleep(random.uniform(5, 10))

if __name__ == "__main__":
    main()