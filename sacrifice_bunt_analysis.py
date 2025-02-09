"""
sacrifice_bunt_analysis.py
Homework 3: Analyzing sacrifice bunting

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script analyzes baseball play-by-play data with a focus on sacrifice bunts and their outcomes.
It calculates the probabilities of different bunt outcomes (missed bunt, unsuccessful sacrifice,
successful sacrifice, and bunt hit) and analyzes run expectancy changes based on a sample dataset.

Usage:
1. Place all relevant play-by-play CSV files in the 'Files' directory.
2. Ensure 'ball_strike_count.csv' and 'run_expectancy.csv' are available in the 'Tables' directory.
3. Run the script to perform analysis and output probabilities, bunt details, and run scoring probabilities for late-inning bunt situations.

Note that for simplicity, you should assume the following:
• A bunt is a sacrifice attempt whenever there are less than two outs and any runner(s) are on base.
• A batter never squares to bunt and takes a ball. Note that the Baseball Reference play-by-play makes it impossible to determine if this occurs.
• If the batter ever fouls or misses a bunt, you should interpret it as the batter fouling/missing the first pitch of the at-bat.
• If a bunt is executed in fair territory, there is never an error that results in runners advancing more than one base, and there is never a double play turned.
• The run expectation table itself necessarily includes bunts; do not make any attempt to unskew this.
"""

import pandas as pd
import os
import glob


def write_to_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Output successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
        # Adding more information to debug
        print(f"Content to write: {content[:500]}...")  # Only show first 500 characters for debugging

# Function to load and aggregate data from all CSV files in the 'Files' directory with error handling
def load_all_play_by_play_data():
    print("\n--- Loading and Aggregating Play-by-Play Data ---")
    try:
        csv_files = glob.glob(os.path.join('Files', '*.csv'))
        if not csv_files:
            print("No CSV files found in 'Files' directory.")
            return pd.DataFrame()  # Return an empty DataFrame if no files are found.

        all_data = pd.concat([pd.read_csv(file, low_memory=False) for file in csv_files], ignore_index=True)
        log = "\n".join([f"Loaded file: {file}" for file in csv_files])
        write_to_file("play_by_play_log.txt", log)  # Writing log to a file
        return all_data
    except Exception as e:
        print(f"Error loading play-by-play data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if something fails

# Function to analyze sacrifice bunt and calculate the run expectancy with error handling and formatted output
def analyze_sacrifice_bunt():
    print("\n--- Analyzing Run Expectancy for Sacrifice Bunt Outcomes ---")
    filepath = os.path.join(os.getcwd(), 'Tables', 'ball_strike_count.csv')

    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    try:
        run_expectancy_data = pd.read_csv(filepath, index_col=0)
        if '0outOXX' not in run_expectancy_data.index or '0-0' not in run_expectancy_data.columns:
            print("Run expectancy data does not contain the required base states.")
            return

        # Initial run expectancy for '0outOXX' with a 0-0 count
        initial_run_expectancy = run_expectancy_data.loc['0outOXX', '0-0']
        print(f"(0outOXX, runner on base):       {initial_run_expectancy:.2f} - (Initial Run Expectancy)")

        # Missed bunt run expectancy change (0outOXX with 0-1 count)
        missed_bunt_run_expectancy = run_expectancy_data.loc['0outOXX', '0-1']
        missed_bunt_change = missed_bunt_run_expectancy - initial_run_expectancy
        print(
            f"(0outOXX, runner on base):       {missed_bunt_run_expectancy:.2f} - (Missed Bunt Run Expectancy, Change: {missed_bunt_change:+.2f})")

        # Unsuccessful sacrifice (runner out, batter safe, 1outOXX, 0-0 count)
        unsuccessful_sacrifice_run_expectancy = run_expectancy_data.loc['1outOXX', '0-0']
        unsuccessful_sacrifice_change = unsuccessful_sacrifice_run_expectancy - initial_run_expectancy
        print(
            f"(1outOXX, runner on base):       {unsuccessful_sacrifice_run_expectancy:.2f} - (Unsuccessful Sacrifice Expectancy, Change: {unsuccessful_sacrifice_change:+.2f})")

        # Successful sacrifice (runner advances, batter out, 1outXOX, 0-0 count)
        successful_sacrifice_run_expectancy = run_expectancy_data.loc['1outXOX', '0-0']
        successful_sacrifice_change = successful_sacrifice_run_expectancy - initial_run_expectancy
        print(
            f"(1outXOX, runner advances):      {successful_sacrifice_run_expectancy:.2f} - (Successful Sacrifice Expectancy, Change: {successful_sacrifice_change:+.2f})")

        # Bunt hit run expectancy (runner and batter safe, 0outOOX, 0-0 count)
        bunt_hit_run_expectancy = run_expectancy_data.loc['0outOOX', '0-0']
        bunt_hit_change = bunt_hit_run_expectancy - initial_run_expectancy
        print(
            f"(0outOOX, runner/batter safe):   {bunt_hit_run_expectancy:.2f} - (Bunt Hit Run Expectancy, Change: {bunt_hit_change:+.2f})")

    except Exception as e:
        print(f"Error analyzing sacrifice bunt: {e}")

# Consolidated function to handle categorizing and logging all bunt and uncategorized bunt situations
def categorize_and_log_bunt_situations(play_by_play_data):
    print("--- Categorizing and Logging Bunt Situations ---")

    # Required columns
    required_columns = ['inning', 'outs', 'runners', 'description']
    if not all(col in play_by_play_data.columns for col in required_columns):
        print("Missing one or more required columns in play-by-play data.")
        return 0, 0  # Return zero if columns are missing

    # Filter for bunt data (less than 2 outs and runners on base)
    bunt_data = play_by_play_data.query(
        'outs < 2 and runners != "---" and description.str.contains("Bunt", case=False, na=False)', engine='python')

    if bunt_data.empty:
        print("No bunt data found.")
        return 0, 0  # Return zero if no bunt data

    # Initialize counters and lists for uncategorized bunts
    uncategorized_bunts = []
    total_bunts = len(bunt_data)

    # Start logging specific bunt situations
    log = ""
    for _, row in bunt_data.iterrows():
        description = row['description'].lower()
        category = "Uncategorized"
        if 'missed' in description or 'foul' in description or 'strikeout' in description:
            category = "Missed Bunt"
        elif 'forceout' in description or 'fielder\'s choice' in description or 'double play' in description:
            category = "Unsuccessful Sacrifice"
        elif ('groundout' in description and 'sacrifice' in description) or ('advances' in description):
            category = "Successful Sacrifice"
        elif 'single' in description or 'bunt hit' in description or 'safe' in description:
            category = "Bunt Hit"
        else:
            uncategorized_bunts.append(row)

        log += f"Inning: {row['inning']}, Outs: {row['outs']}, Runners: {row['runners']}, Description: {row['description']}, Category: {category}\n"

    # Log total bunt situations
    log += f"\n--- Total Specific Bunt Situations: {total_bunts} ---\n"

    # Handle uncategorized bunt situations
    total_uncategorized = len(uncategorized_bunts)
    log += f"\n--- Total Uncategorized Bunt Situations: {total_uncategorized} ---\n"

    # Write specific bunt situations to file
    write_to_file("bunt_situations.txt", log)

    # Handle categorizing uncategorized bunt situations
    categorize_uncategorized_bunts(uncategorized_bunts)

    print(f"\n--- Summary ---")
    print(f"Total Specific Bunt Situations: {total_bunts}")
    print(f"Total Uncategorized Bunt Situations: {total_uncategorized}")

    return total_bunts, total_uncategorized

# Helper function to categorize and log uncategorized bunt situations
def categorize_uncategorized_bunts(uncategorized_bunts):
    log = ""

    # Grouping by categories using a dictionary for simplicity
    categories = {
        "errors_e1": [],
        "popflies": [],
        "lineouts": [],
        "interference": [],
        "groundouts": [],
        "doubles": []
    }

    # Categorizing each uncategorized bunt situation
    for row in uncategorized_bunts:
        description = row['description'].lower()
        if 'reached on e1' in description:
            categories['errors_e1'].append(row)
        elif 'popfly' in description:
            categories['popflies'].append(row)
        elif 'lineout' in description:
            categories['lineouts'].append(row)
        elif 'interference' in description:
            categories['interference'].append(row)
        elif 'groundout' in description:
            categories['groundouts'].append(row)
        elif 'double' in description:
            categories['doubles'].append(row)

    # Writing categorized situations to the log with explanations
    total_uncategorized = len(uncategorized_bunts)
    log += f"\nTotal Uncategorized Bunt Situations: {total_uncategorized}\n"

    for category, rows in categories.items():
        if rows:
            log += f"\nCategory: {category} ({len(rows)} situations)\n"
            for row in rows:
                log += f"Inning: {row['inning']}, Outs: {row['outs']}, Runners: {row['runners']}, Description: {row['description']}\n"

    # Write uncategorized bunt situations to file
    write_to_file("uncategorized_bunt_situations.txt", log)

# Function to calculate the bunt outcome probabilities (X, Y, Z, W)
def calculate_bunt_probabilities_with_assumptions(play_by_play_data):
    print("\n--- Calculating Bunt Outcome Probabilities (X, Y, Z, W) ---")

    bunt_data = play_by_play_data.query('outs < 2 and runners != "---"')

    if bunt_data.empty:
        print("No bunt data found.")
        return 0, 0, 0, 0, pd.DataFrame()

    # X: Missed bunt, foul bunt, or strikeout treated as first pitch miss
    missed_bunts = bunt_data['description'].str.contains('missed|foul|strikeout', case=False, na=False).sum()
    total_bunts = len(bunt_data)

    X = missed_bunts / total_bunts if total_bunts else 0

    # If bunt is in play (1 - X)
    bunt_in_play_data = bunt_data[~bunt_data['description'].str.contains('missed|foul|strikeout', case=False, na=False)]

    # Y: Unsuccessful sacrifice (runner out at second, batter safe at first)
    unsuccessful_sacrifice = bunt_in_play_data['description'].str.contains('forceout|fielder\'s choice|double play',
                                                                           case=False,
                                                                           na=False).sum()

    # Z: Successful sacrifice (runner advances to second, batter out at first)
    successful_sacrifice = bunt_in_play_data['description'].str.contains('groundout.*sacrifice|advances', case=False,
                                                                         na=False).sum()

    # W: Bunt hit (runner advances, batter safe at first)
    bunt_hit = bunt_in_play_data['description'].str.contains('single|bunt hit|safe', case=False, na=False).sum()

    total_in_play_bunts = len(bunt_in_play_data)

    Y = unsuccessful_sacrifice / total_in_play_bunts if total_in_play_bunts else 0
    Z = successful_sacrifice / total_in_play_bunts if total_in_play_bunts else 0
    W = bunt_hit / total_in_play_bunts if total_in_play_bunts else 0

    print(f"X = {X:.4f}, Y = {Y:.4f}, Z = {Z:.4f}, W = {W:.4f}")
    return X, Y, Z, W, bunt_data

# Function to calculate the optimistic upper bound strategy
def optimistic_upper_bound_bunt_strategy(play_by_play_data):
    print("\n--- Calculating Optimistic Upper Bound for Bunt Strategy ---")

    # Set X to zero and calculate W based on bunts with no runners on base
    no_runner_bunts = play_by_play_data.query('runners == "---" and description.str.contains("Bunt", case=False, na=False)')
    if no_runner_bunts.empty:
        print("No bunt data found with no runners on base.")
        return 0, 0, 0, 0

    # W is based on bunts with no runners on base
    total_no_runner_bunts = len(no_runner_bunts)
    bunt_hits_no_runners = no_runner_bunts['description'].str.contains('single|bunt hit|safe', case=False, na=False).sum()

    W = bunt_hits_no_runners / total_no_runner_bunts if total_no_runner_bunts else 0
    X = 0

    # Scale Y and Z downward equally to ensure sum is 1
    Y, Z = (1 - W) / 2, (1 - W) / 2

    print(f"X = {X}, Y = {Y:.4f}, Z = {Z:.4f}, W = {W:.4f} (Optimistic Scenario)")
    return X, Y, Z, W

# Function to restore X and use updated W, Y, and Z
def recalculate_with_original_X(X_original, W_optimistic, play_by_play_data):
    print("\n--- Recalculating with Original X and Updated W ---")

    # Scale Y and Z downward to ensure the sum is 1
    Y, Z = (1 - (X_original + W_optimistic)) / 2, (1 - (X_original + W_optimistic)) / 2

    print(f"X = {X_original}, Y = {Y:.4f}, Z = {Z:.4f}, W = {W_optimistic:.4f} (Using Optimistic W)")
    return X_original, Y, Z, W_optimistic

# Function to analyze bunt effects on scoring probabilities (8th inning or later)
def analyze_bunt_run_probability(play_by_play_data, run_expectancy_data):
    print("\n--- Analyzing Bunt Effects on Probability of Scoring At Least One Run ---")

    # Convert 'inning' column to numeric (integer), errors='coerce' will handle any invalid values
    play_by_play_data['inning_numeric'] = pd.to_numeric(play_by_play_data['inning'], errors='coerce')

    # Filter data for runners on 2nd or on 1st and 2nd, no outs, and 8th inning or later
    relevant_bunt_data = play_by_play_data[(play_by_play_data['outs'] == 0) &
                                           (play_by_play_data['runners'].str.contains('2|12')) &
                                           (play_by_play_data['inning_numeric'] >= 8) &
                                           play_by_play_data['description'].str.contains('Bunt', case=False, na=False)]

    # Initialize counters for each outcome in the late-inning bunt data
    total_bunts = len(relevant_bunt_data)
    successful_bunts = relevant_bunt_data['description'].str.contains('sacrifice|groundout', case=False, na=False).sum()
    unsuccessful_bunts = relevant_bunt_data['description'].str.contains('missed|foul|unsuccessful', case=False, na=False).sum()
    bunt_hits = relevant_bunt_data['description'].str.contains('single|bunt hit', case=False, na=False).sum()

    # Calculate probabilities of each outcome
    Y = unsuccessful_bunts / total_bunts if total_bunts > 0 else 0
    Z = successful_bunts / total_bunts if total_bunts > 0 else 0
    W = bunt_hits / total_bunts if total_bunts > 0 else 0

    print(f"\nTotal bunts in 8th inning or later: {total_bunts}")
    print(f"Unsuccessful bunt probability (Y): {Y}")
    print(f"Successful bunt probability (Z): {Z}")
    print(f"Bunt hit probability (W): {W}")

    # Handle missing values in 'Baes States' and 'Run Expectancy' by dropping NaN entries
    run_expectancy_data = run_expectancy_data.dropna(subset=['Baes States', 'Run Expectancy'])

    if total_bunts > 0:
        run_prob = run_expectancy_data.loc[run_expectancy_data['Baes States'].str.contains('_2_|12_'), 'Run Expectancy']
        if not run_prob.empty:
            print(f"Probability of scoring at least one run after bunt: {run_prob.values[0]}")
        else:
            print("No run expectancy data available for these situations.")
    else:
        print("No relevant bunt situations found in the data.")

    return Y, Z, W


if __name__ == '__main__':
    print("\n=== Sacrifice Bunt Analysis ===")
    play_by_play_data = load_all_play_by_play_data()

    if not play_by_play_data.empty:  # Ensure there is data to work with
        analyze_sacrifice_bunt()

        print("\n=== Categorizing Bunt Situations ===")
        total_bunts, total_uncategorized = categorize_and_log_bunt_situations(play_by_play_data)

        print("\n=== Recalculating Probabilities ===")
        X_final, Y_final, Z_final, W_final, updated_bunt_data = calculate_bunt_probabilities_with_assumptions(
            play_by_play_data)

        print("\n=== Optimistic Upper Bound Bunt Strategy ===")
        X_opt, Y_opt, Z_opt, W_opt = optimistic_upper_bound_bunt_strategy(play_by_play_data)

        print("\n=== Restoring Original X with Optimistic W ===")
        X_restored, Y_restored, Z_restored, W_restored = recalculate_with_original_X(X_final, W_opt, play_by_play_data)

        print("\n=== Late Inning Run Probability Analysis ===")
        run_expectancy_filepath = os.path.join(os.getcwd(), 'Tables', 'run_expectancy.csv')
        if os.path.exists(run_expectancy_filepath):
            run_expectancy_data = pd.read_csv(run_expectancy_filepath)
            analyze_bunt_run_probability(play_by_play_data, run_expectancy_data)
        else:
            print(f"Error: {run_expectancy_filepath} not found.")
    else:
        print("Error: No play-by-play data loaded.")