"""
createPBP.py
Author: Christopher Reid

This script generates limited play-by-play (PBP) data for NFL games from the 2014 to 2023 seasons.
For each game, it extracts specific fields relevant to analyzing momentum and saves the data to
separate CSV files, one per game, in a directory called 'NFLCSV'.

Fields included in each CSV file:
    - play_id: Unique identifier for each play.
    - drive_play_id_started: Identifier of the first play in the drive.
    - half_seconds_remaining: Time remaining in the half (in seconds).
    - yardline_100: Distance from the offense’s goal line (0 = goal line, 100 = opponent’s goal line).
    - down: The down number for the play (1st, 2nd, 3rd, or 4th).
    - ydstogo: Yards to go for a first down.
    - score_differential: Difference in score between the teams.
    - drive_start_transition: The event that started the drive (e.g., kickoff, turnover).
    - fixed_drive_result: Outcome of the drive (e.g., touchdown, punt, field goal).
    - game_id: Unique identifier for each game, used to create individual CSV files.

Directory Structure:
    - Output directory: 'NFLCSV' (created if it does not exist)
    - Each game’s data is saved as a CSV file in 'NFLCSV', named in the format 'season_gameid.csv'
      (e.g., '2014_1001.csv' for game ID 1001 in the 2014 season).

Requirements:
    - Python 3.x
    - pandas library (install with `pip install pandas`)
    - nfl_data_py library (install with `pip install nfl_data_py`)

Usage:
    Run the script from the command line or an IDE. Ensure any necessary setup for nfl_data_py
    is completed before running the script.
"""

import os
import nfl_data_py as nfl

def create_output_directory(directory="NFLCSV"):
    """Creates the output directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def save_game_data(season, game_id, game_data, output_dir="NFLCSV"):
    """Saves play-by-play data for a single game to a CSV file."""
    output_file = os.path.join(output_dir, f"{season}_{game_id}.csv")
    game_data.to_csv(output_file, index=False)
    print(f"Saved {output_file}")


def process_season(season, output_dir="NFLCSV"):
    """Processes play-by-play data for a given season and saves each game as a separate CSV."""
    pbp_data = nfl.import_pbp_data([season])

    # Check if 'game_id' column exists
    if 'game_id' not in pbp_data.columns:
        raise KeyError("'game_id' column is missing from the play-by-play data. Check nfl_data_py data fields.")

    # Filter relevant fields
    pbp_filtered = pbp_data[[
        'play_id', 'drive_play_id_started', 'half_seconds_remaining',
        'yardline_100', 'down', 'ydstogo', 'score_differential',
        'drive_start_transition', 'fixed_drive_result', 'game_id'
    ]]

    # Save each game’s data to a CSV file
    for game_id in pbp_filtered['game_id'].unique():
        game_data = pbp_filtered[pbp_filtered['game_id'] == game_id]
        save_game_data(season, game_id, game_data, output_dir)


def main():
    """Main function to process multiple seasons and save play-by-play data."""
    output_dir = "NFLCSV"
    create_output_directory(output_dir)

    seasons = range(2014, 2024)
    for season in seasons:
        process_season(season, output_dir)


if __name__ == "__main__":
    main()