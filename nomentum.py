"""
nomentum.py

This program analyzes NFL play-by-play data to identify and evaluate drives that meet specific criteria.
Given a directory of play-by-play files (one per game), it filters drives based on:
    - Minimum time remaining in either half
    - Starting yard line (distance from the end zone for the team with possession)
    - Maximum score differential
    - Method of possession change (e.g., "PUNT", "FUMBLE")

For each drive that meets these criteria, the program records the result and calculates the percentage of
times each unique outcome occurred.

Usage:
    python nomentum.py <directory> <min_time_remaining> <yard_line> <max_score_diff> <possession_change_type>

Command-line Parameters:
    - directory: The directory containing play-by-play CSV files.
    - min_time_remaining: Minimum time remaining in the half for a drive to be considered (in seconds).
    - yard_line: Yard line threshold (distance from the end zone for the team with possession).
    - max_score_diff: Maximum score differential for a drive to be considered.
    - possession_change_type: Method of possession change as a string (e.g., "PUNT").

Output:
    - Lists each unique drive result with its count and percentage, sorted alphabetically by result name.
    - Provides a total count of considered drives.

Author: [Your Name]
Date: [Date]
"""

import os
import sys
import pandas as pd

def load_play_by_play_files(directory):
    """Loads all CSV files from the specified directory and concatenates them into a single DataFrame."""
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            game_data = pd.read_csv(file_path)
            all_data.append(game_data)
    return pd.concat(all_data, ignore_index=True)


def filter_drives(data, min_time, yard_line, max_score_diff, possession_change_type):
    """
    Filters the drives based on the specified criteria:
    - Time remaining in the half >= min_time
    - Yard line <= yard_line
    - Score differential <= max_score_diff
    - Drive start method matches possession_change_type (e.g., "PUNT")
    - Drive start identified by play_id == drive_play_id_started
    """
    # Filter drives based on specified criteria, considering only drive start rows
    filtered_data = data[
        (data['play_id'] == data['drive_play_id_started']) &  # Identifies drive starts
        (data['half_seconds_remaining'] >= min_time) &
        (data['yardline_100'] >= yard_line) &
        (data['score_differential'] <= max_score_diff) &
        (data['drive_start_transition'] == possession_change_type)
    ]
    return filtered_data


def analyze_drive_results(filtered_data):
    """
    Analyzes the results of each considered drive and calculates the frequency and percentage
    of each unique result.
    """
    # Count each drive result
    results = filtered_data['fixed_drive_result'].value_counts()
    total_drives = results.sum()

    # Prepare a sorted list of results with counts and percentages
    result_percentages = [
        (result, count, (count / total_drives) * 100)
        for result, count in results.items()
    ]

    # Sort alphabetically by drive result
    result_percentages.sort(key=lambda x: x[0])

    return result_percentages, total_drives


def main():
    # Parse command-line arguments
    if len(sys.argv) != 6:
        print("Usage: python nomentum.py <directory> <min_time_remaining> <yard_line> <max_score_diff> <possession_change_type>")
        sys.exit(1)

    directory = sys.argv[1]
    min_time_remaining = int(sys.argv[2])
    yard_line = int(sys.argv[3])
    max_score_diff = int(sys.argv[4])
    possession_change_type = sys.argv[5].upper()  # Ensure input is uppercase for consistency

    # Load and filter the play-by-play data
    data = load_play_by_play_files(directory)
    filtered_data = filter_drives(data, min_time_remaining, yard_line, max_score_diff, possession_change_type)

    # Analyze drive results and print percentages
    result_percentages, total_drives = analyze_drive_results(filtered_data)

    # Print the results in the desired format
    for result, count, percentage in result_percentages:
        print(f"{result}: {count} ({percentage:.2f}%)")
    print(f"Total: {total_drives}")


if __name__ == "__main__":
    main()