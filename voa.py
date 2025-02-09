"""
File: value_over_average.py
Author: [Your Name]
Date: [Today's Date]
Description:
    This script calculates "Value Over Average" for NFL teams by analyzing their play-by-play performance
    and comparing each team's success to the league average in various field position zones.
    It assigns success points to each play based on yards gained, turnovers, and touchdowns. By grouping plays
    according to yardline position, the script determines team performance differentials from the average,
    allowing insight into each team's ability to exceed expectations in specific field zones.

Usage:
    Run this script with nfl_data_py installed and ensure access to 2023 NFL play-by-play data.
    It will output team success point differentials and play counts by field position group.

Data Source:
    Uses nfl_data_py to fetch NFL play-by-play data for the 2023 season.

Key Functions:
    - get_yardline_group(yardline): Determines the field position group based on yardline.
    - calculate_success_points(play): Calculates success points for a play based on yards gained,
      down, and turnover status.

Output:
    - Displays each NFL team's success point differential from the league average.
    - Shows the number of plays categorized by field position groups.

Requirements:
    - Python 3.x
    - pandas
    - nfl_data_py
    - numpy

"""

import sys
import pandas as pd
import nfl_data_py as nfl
from collections import defaultdict
import numpy as np


def get_yardline_group(yardline):
    if 1 <= yardline <= 20:
        return 1  # Deep in own territory
    elif 21 <= yardline <= 39:
        return 2  # Own territory
    elif 40 <= yardline <= 59:
        return 3  # Midfield
    elif 60 <= yardline <= 79:
        return 4  # Opponent territory
    elif 80 <= yardline <= 99:
        return 5  # Red zone
    else:
        return None  # Invalid yardline


def calculate_success_points(play):
    # Check for turnovers first
    if play['interception'] == 1:
        return -3
    if play['fumble'] == 1:
        return -1.5

    yards_gained = play['yards_gained']
    down = play['down']
    ydstogo = play['ydstogo']

    # Calculate base success points
    # Handle special cases first
    if yards_gained <= -3:
        base_points = -1
    elif yards_gained >= 40:
        base_points = 5
    elif 20 <= yards_gained <= 39:
        base_points = 4
    elif 11 <= yards_gained <= 19:
        base_points = 3
    elif yards_gained < -2:
        base_points = -1
    # Handle the smooth function case (-2 to 10 yards)
    elif -2 <= yards_gained <= 10:
        # Different thresholds based on down
        if down == 1:
            threshold = 0.40 * ydstogo
        elif down == 2:
            threshold = 0.65 * ydstogo
        else:  # down 3 or 4
            threshold = ydstogo

        if yards_gained >= threshold:
            # Linear interpolation between threshold (1 point) and 10 yards (3 points)
            if yards_gained <= 10:
                # Handle case where threshold equals 10
                if threshold >= 10:
                    base_points = 3  # Already reached the maximum for this range
                else:
                    base_points = 1 + 2 * (yards_gained - threshold) / (10 - threshold)
            else:
                base_points = 3
        else:
            # Linear interpolation between -2 (0 points) and threshold (1 point)
            denominator = threshold + 2
            if denominator == 0:  # Just in case, though this shouldn't happen
                base_points = 0
            else:
                base_points = (yards_gained + 2) / denominator
    else:
        base_points = 0  # Fallback case

    # Add touchdown bonus
    if play['touchdown'] == 1:
        base_points += 1

    return base_points

# Load play-by-play data
pbp = nfl.import_pbp_data([2023], downcast=True, cache=False, alt_path=None)

# Initialize dictionaries
play_dict = defaultdict(list)
success_averages = defaultdict(float)
play_counts = defaultdict(int)
team_success_diff = defaultdict(float)

# First pass: Process each play and calculate success points
for _, play in pbp.iterrows():
    # Skip incomplete or buggy plays
    if pd.isna(play['yardline_100']) or pd.isna(play['down']) or \
       pd.isna(play['ydstogo']) or pd.isna(play['yards_gained']) or \
       pd.isna(play['play_type']) or pd.isna(play['posteam']) or \
       pd.isna(play['interception']) or pd.isna(play['fumble']) or \
       pd.isna(play['touchdown']):
        continue

    # Get yardline group
    yardline_group = get_yardline_group(play['yardline_100'])

    # Skip if yardline group is None
    if yardline_group is None:
        continue

    # Get down and distance information
    down = play['down']
    ydstogo = play['ydstogo']

    # Calculate success points for the play
    success_points = calculate_success_points(play)

    # Store play information in play_dict for the team and yardline group
    team = play['posteam']
    play_dict[(team, yardline_group)].append(success_points)

    # Update play counts and cumulative success points for averages
    play_counts[yardline_group] += 1
    success_averages[yardline_group] += success_points

# Calculate averages for each yardline group
for yardline_group, total_points in success_averages.items():
    if play_counts[yardline_group] > 0:
        success_averages[yardline_group] = total_points / play_counts[yardline_group]

# Second pass: Calculate team differences from the average
for (team, yardline_group), points_list in play_dict.items():
    # Calculate the team's average success points for this yardline group
    team_average = sum(points_list) / len(points_list)

    # Get the league average success points for this yardline group
    league_average = success_averages[yardline_group]

    # Calculate the differential and add it to the team's total
    team_success_diff[team] += team_average - league_average

# Output results sorted by success differential
sorted_teams = sorted(team_success_diff.items(), key=lambda x: x[1], reverse=True)
print("\nTeam Success Point Differentials:")
print("=" * 40)
print(f"{'Team':<5} {'Differential':>15}")
print("-" * 40)
for team, diff in sorted_teams:
    print(f"{team:<5} {diff:>15.2f}")

# Optional: Print statistics about the groupings
print("\nPlays per field position group:")
group_counts = defaultdict(int)
for key in play_counts:
    yardline_group = key[0]
    group_counts[yardline_group] += play_counts[key]

print("\nField Position Groups:")
print("1: Own 1-20  (Deep)")
print("2: Own 21-39 (Own territory)")
print("3: 40-59     (Midfield)")
print("4: 60-79     (Opponent territory)")
print("5: 80-99     (Red zone)")
print("\nPlay counts by group:")
for group in sorted(group_counts.keys()):
    print(f"Group {group}: {group_counts[group]} plays")