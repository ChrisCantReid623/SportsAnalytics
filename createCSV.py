"""
createCSV.py
Author: Christopher Reid

This script generates play-by-play data CSV files (one per game) for NFL seasons 2001-2023.
Each file includes at least the following fields:
    - win probability (wp)
    - team on offense (posteam)
    - team on defense (defteam)
    - score differential after the play (score differential post)
    - winner (1 if offensive team won, 0 otherwise)

The 'winner' field is not available in the raw data and is determined based on the final score.
The script creates an 'NFLCSV' directory if it does not exist, saving all game files there.

"""

import os
import pandas as pd
import nfl_data_py as nfl

def create_csv_files(start_season, end_season, output_dir="NFLCSV"):
    # Fetch play-by-play data for the specified seasons
    print(f"Fetching play-by-play data for seasons {start_season}-{end_season}...")
    pbp_data = nfl.import_pbp_data(range(start_season, end_season + 1))

    # Ensure required columns exist
    required_columns = {'wp', 'posteam', 'defteam', 'posteam_score', 'defteam_score', 'game_id', 'play_id'}
    if not required_columns.issubset(pbp_data.columns):
        raise ValueError("The fetched data is missing required columns.")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Group the data by game_id to process each game separately
    for game_id, game_data in pbp_data.groupby('game_id'):
        try:
            # Sort game data by play order
            game_data = game_data.sort_values(by='play_id')

            # Get the last play of the game
            last_play = game_data.iloc[-1]

            # Determine the winner based on the final score
            posteam_score = last_play['posteam_score']
            defteam_score = last_play['defteam_score']
            posteam = last_play['posteam']

            if posteam_score > defteam_score:
                winner_value = 1  # Offensive team wins
            else:
                winner_value = 0  # Defensive team wins

            # Add the winner column to the entire game data
            game_data['winner'] = winner_value

            # Select required columns for the output
            output_columns = ['wp', 'posteam', 'defteam', 'posteam_score', 'defteam_score', 'score_differential_post', 'winner']
            game_data = game_data[output_columns]

            # Generate a filename using the season and teams involved
            season = game_data['posteam'].iloc[0]
            home_team = last_play['home_team'] if 'home_team' in last_play else 'UNK'
            away_team = last_play['away_team'] if 'away_team' in last_play else 'UNK'
            filename = f"{season}_{game_id}_{away_team}_{home_team}.csv"

            # Save the processed game data to a CSV file
            output_path = os.path.join(output_dir, filename)
            game_data.to_csv(output_path, index=False)
            print(f"Processed game: {filename}")

        except Exception as e:
            print(f"Error processing game {game_id}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python createCSV.py <start_season> <end_season>")
        sys.exit(1)

    start_season = int(sys.argv[1])
    end_season = int(sys.argv[2])

    # Create CSV files for the specified seasons
    create_csv_files(start_season, end_season)