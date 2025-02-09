"""
calculateBlownGames.py
Author: Christopher Reid

This script analyzes "blown games" from play-by-play data in CSV files generated for each NFL game.
It takes three command-line arguments:
    1. Directory where all generated CSV files are located.
    2. lowerWPThreshold - a lower win probability threshold (float between 0.0 and 1.0).
    3. upperWPThreshold - an upper win probability threshold (float between 0.0 and 1.0).

For each team, if their win probability was between lowerWPThreshold and upperWPThreshold
at any point during a game, we count that game in gamesBetweenThresholds. If the team
ultimately won the game, we also count it in gamesWon.

After processing, the script outputs:
    Team Name, gamesBetweenThresholds, gamesWon, Winning Percentage (rounded to two decimals),
    sorted by Winning Percentage in descending order.
"""

import os
import sys
import pandas as pd
from collections import defaultdict

def calculate_blown_games(directory, lower_wp_threshold, upper_wp_threshold):
    # Dictionaries to count games between thresholds and games won
    games_between_thresholds = defaultdict(int)
    games_won = defaultdict(int)

    # Iterate through all CSV files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)

            try:
                # Read the CSV file into a pandas DataFrame
                game_data = pd.read_csv(file_path)

                # Ensure required columns exist
                required_columns = {'wp', 'posteam', 'winner'}
                if not required_columns.issubset(game_data.columns):
                    print(f"Skipping {filename}: Missing required columns.")
                    continue

                # Track teams that had a win probability in the threshold range during the game
                teams_within_threshold = set()
                teams_that_won = set()

                for _, row in game_data.iterrows():
                    team = row['posteam']
                    win_probability = row['wp']
                    winner = row['winner']

                    # Check if the win probability is within the thresholds
                    if lower_wp_threshold <= win_probability <= upper_wp_threshold:
                        teams_within_threshold.add(team)

                        # Check if the team ultimately won the game
                        if winner == 1:
                            teams_that_won.add(team)

                # Update the counts for each team
                for team in teams_within_threshold:
                    games_between_thresholds[team] += 1
                    if team in teams_that_won:
                        games_won[team] += 1

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Calculate the ratio R and prepare the results
    results = []
    for team in games_between_thresholds:
        between_threshold_count = games_between_thresholds[team]
        won_count = games_won[team]
        ratio_r = (won_count / between_threshold_count) * 100 if between_threshold_count > 0 else 0
        results.append((team, between_threshold_count, won_count, ratio_r))

    # Sort results by R in descending order
    results.sort(key=lambda x: x[3], reverse=True)

    # Print the results with a header
    print("Team, Games Between Thresholds, Games Won, Winning Percentage")
    for team, between_threshold_count, won_count, ratio_r in results:
        print(f"{team}, {between_threshold_count}, {won_count}, {ratio_r:.2f}%")

if __name__ == "__main__":
    # Validate command-line arguments
    if len(sys.argv) < 4:
        print("Usage: python calculateBlownGames.py <directory> <lowerWPThreshold> <upperWPThreshold>")
        sys.exit(1)

    # Parse command-line arguments
    directory = sys.argv[1]
    lower_wp_threshold = float(sys.argv[2])
    upper_wp_threshold = float(sys.argv[3])

    if not (0.0 <= lower_wp_threshold < upper_wp_threshold <= 1.0):
        print("Error: Thresholds must be between 0.0 and 1.0, with lowerWPThreshold < upperWPThreshold.")
        sys.exit(1)

    # Run the blown games calculation
    calculate_blown_games(directory, lower_wp_threshold, upper_wp_threshold)