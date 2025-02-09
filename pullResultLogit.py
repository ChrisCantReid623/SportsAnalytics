"""
pullResultLogit.py
Investigating the Effect of Pulling the Ball on OPS

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script calculates the OPS (On-base Plus Slugging) for hitters, separating results for left-handed
and right-handed hitters. It parses batted ball events to determine hits and total bases.

It takes in either a single CSV file or processes all CSV files in a specified directory. For each file, it outputs three OPS values:
1. OPS for all hitters
2. OPS for left-handed hitters
3. OPS for right-handed hitters

Usage:
Run the script and provide a CSV file as input, or specify a directory to process all CSV files in the directory.

Example command to process a single file:
$ python pullResultLogit.py all2024.csv

Example command to process all CSV files in a directory:
$ python pullResultLogit.py ./relative_directory_path
"""

import pandas as pd
import sys
import os

# Helper function to determine the number of bases earned from the 'events' field
def get_total_bases(event):
    if event == 'single':
        return 1
    elif event == 'double':
        return 2
    elif event == 'triple':
        return 3
    elif event == 'home_run':
        return 4
    else:
        return 0  # For events like field_out, ground_out, etc.

# Function to compute OBP (On-base Percentage)
def calculate_obp(data):
    hits = data['hits'].sum()
    plate_appearances = data.shape[0]  # Each row is one plate appearance
    return hits / plate_appearances if plate_appearances > 0 else 0

# Function to compute SLG (Slugging Percentage)
def calculate_slg(data):
    total_bases = data['total_bases'].sum()
    plate_appearances = data.shape[0]
    return total_bases / plate_appearances if plate_appearances > 0 else 0

# Function to compute OPS (OBP + SLG)
def calculate_ops(data):
    obp = calculate_obp(data)
    slg = calculate_slg(data)
    return obp + slg

# Function to parse events and add 'hits' and 'total_bases' columns
def process_data(data):
    # Determine if the event was a hit and the corresponding total bases
    data['hits'] = data['events'].apply(lambda x: 1 if x in ['single', 'double', 'triple', 'home_run'] else 0)
    data['total_bases'] = data['events'].apply(get_total_bases)
    return data

# Function to calculate and print OPS for all, left-handed, and right-handed hitters
def compute_and_print_ops(data, filename):
    # Parse the data to add hits and total_bases columns
    data = process_data(data)

    print(f"--- OPS Results for {filename} ---")

    # OPS for all hitters
    ops_all = calculate_ops(data)
    print(f"OPS for all hitters: {ops_all:.3f}")

    # OPS for left-handed hitters
    left_handed = data[data['stand'] == 'L']  # 'stand' refers to batter stance (L for left, R for right)
    ops_lefties = calculate_ops(left_handed)
    print(f"OPS for left-handed hitters: {ops_lefties:.3f}")

    # OPS for right-handed hitters
    right_handed = data[data['stand'] == 'R']
    ops_righties = calculate_ops(right_handed)
    print(f"OPS for right-handed hitters: {ops_righties:.3f}")

# Alternative main function that processes all CSV files in the same directory as the Python script
def main_directory():
    # Get the current directory where the script is located
    directory_path = os.getcwd()

    # Print the directory being used
    print(f"Processing all CSV files in directory: {directory_path}")

    # Iterate through all files in the current directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory_path, filename)
            print(f"\nProcessing file: {filepath}")

            # Load the data from the CSV file
            data = pd.read_csv(filepath)

            # Compute and print the OPS values with better labeling
            compute_and_print_ops(data, filename)

# Original main function for single CSV file input
def main_single_file():
    # Ensure the script receives a CSV filename as input
    if len(sys.argv) != 2:
        print("Usage: python pullResultLogit.py <csv_file> or <directory_path>")
        sys.exit(1)

    # Get the CSV filename or directory path from the command line
    path = sys.argv[1]

    # Check if the input is a directory or a file
    if os.path.isdir(path):
        # Call the alternative main function to process all files in the directory
        main_directory(path)
    else:
        # Process the single file
        print(f"Processing file: {path}")
        data = pd.read_csv(path)
        compute_and_print_ops(data, path)

if __name__ == "__main__":
    main_single_file()