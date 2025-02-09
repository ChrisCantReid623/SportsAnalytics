import requests
from bs4 import BeautifulSoup, Comment
import re
import csv
import time
import os

# Function to scrape the league schedule and collect all box score URLs
def get_game_urls(league_schedule_url):
    base_url = 'https://www.baseball-reference.com'
    response = requests.get(league_schedule_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the box score links
    game_links = []
    for a in soup.find_all('a', href=True, string='Boxscore'):
        game_links.append(base_url + a['href'])

    return game_links

# Function to scrape a single game's play-by-play data
def scrape_single_game(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract commented-out sections that contain play-by-play data
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    for comment in comments:
        if 'play_by_play' in comment:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            tables = comment_soup.find_all('table')
            for table in tables:
                if 'play_by_play' in table.get('id', ''):
                    return table

# Function to clean the "Pitch Code" column
def clean_pitch_code(pitch_code):
    # Remove everything after the closing parenthesis
    return re.sub(r'\)(.*)', ')', pitch_code)

# Function to extract and format inning and play-by-play data into a list of dictionaries
def extract_inning_info(table):
    inning = ""
    data = []
    for row in table.find_all('tr'):
        # Check if the row contains inning information
        inning_cell = row.find('th', {'data-stat': 'inning'})
        if inning_cell:
            inning = inning_cell.text.strip()  # Get the inning information (e.g., 't1', 'b1')

        cols = [td.text.strip() for td in row.find_all('td')]
        if len(cols) >= 10:  # Only process rows with sufficient columns
            # Clean up special characters using regular expressions or replace()
            cleaned_cols = [re.sub(r'[^\x00-\x7F]+', '', col) for col in cols]

            # Clean up the "Pitch Code" column
            cleaned_pitch_code = clean_pitch_code(cleaned_cols[3])

            play = {
                "Inning": inning,
                "Score": cleaned_cols[0],
                "Outs": cleaned_cols[1],
                "Runners": cleaned_cols[2],
                "Pitch Code": cleaned_pitch_code,
                "Runs Scored": cleaned_cols[4],
                "Team": cleaned_cols[5],
                "Batter": cleaned_cols[6],
                "Pitcher": cleaned_cols[7],
                "Change WP": cleaned_cols[8],
                "Current WP": cleaned_cols[9],
                "Description": cleaned_cols[10] if len(cleaned_cols) > 10 else ""
            }
            data.append(play)
    return data

# Function to write the play-by-play data to CSV with an index column
def write_to_csv(data, filename='play_by_play.csv'):
    headers = ["Index", "Inning", "Score", "Outs", "Runners", "Pitch Code", "Runs Scored", "Team", "Batter", "Pitcher",
               "Change WP", "Current WP", "Description"]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for idx, row in enumerate(data, start=1):
            row_with_index = {"Index": idx, **row}  # Add index to each row
            writer.writerow(row_with_index)

# Function to check if the game URL has already been processed
def is_url_processed(url):
    processed_file = os.path.join(os.path.dirname(__file__), "processed_games.txt")
    try:
        with open(processed_file, "r") as file:
            processed_urls = file.read().splitlines()
            return url in processed_urls
    except FileNotFoundError:
        return False

# Function to mark a URL as processed
def mark_url_as_processed(url):
    processed_file = os.path.join(os.path.dirname(__file__), "processed_games.txt")
    with open(processed_file, "a") as file:
        file.write(url + "\n")

# Main function to scrape all games and write the play-by-play data to a CSV
def scrape_all_games(league_schedule_url):
    game_urls = get_game_urls(league_schedule_url)
    all_play_data = []

    for i, game_url in enumerate(game_urls, start=1):  # Using enumerate to track the count
        if is_url_processed(game_url):
            print(f"Skipping already processed game: {game_url}")
            continue

        print(f"{i}. Scraping play-by-play data from {game_url}")  # Added counter to the print statement
        table = scrape_single_game(game_url)
        if table:
            play_data = extract_inning_info(table)
            if play_data:
                all_play_data.extend(play_data)  # Add data from each game to the overall list
                mark_url_as_processed(game_url)
            else:
                print(f"No play-by-play data found for {game_url}")
        else:
            print(f"No play-by-play data found for {game_url}")

        time.sleep(5)  # Delay to avoid getting blocked by Baseball Reference

    if all_play_data:
        write_to_csv(all_play_data)
    else:
        print("No play-by-play data to write.")

# Example league schedule URL (2023 season)
league_schedule_url = 'https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml'

# Run the main scraping function
scrape_all_games(league_schedule_url)
