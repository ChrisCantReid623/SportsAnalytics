"""
hitDistanceAnalysis.py
Investigating the Effect of Pulling the Ball on Fly Ball Distance

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script calculates the effect of pulling the ball on fly ball distance. It filters fly balls from
two input files: one for pulled balls and one for balls hit to the opposite field.

It outputs the following values (each on a separate line):
1. Total number of fly balls
2. Number of pulled fly balls
3. Average distance of pulled fly balls
4. Number of fly balls hit to the opposite field
5. Average distance of fly balls hit to the opposite field

Usage:
Run the script with two command-line arguments: the pulled balls file and the opposite field balls file.

Example command:
$ python hitDistanceAnalysis.py pull2024.csv oppo2024.csv
"""

import sys
import pandas as pd

# Helper function to filter only fly balls
def filter_fly_balls(data):
    return data[data['bb_type'] == 'fly_ball']

# Function to calculate the average distance of fly balls
def calculate_average_distance(data):
    return data['hit_distance_sc'].mean() if not data.empty else 0

# Main function to handle input and output
def main():
    # Ensure the script receives two CSV filenames as input
    if len(sys.argv) != 3:
        print("Usage: python hitDistanceAnalysis.py <pulled_balls_file> <opposite_field_file>")
        sys.exit(1)

    # Get the filenames from the command line
    pulled_file = sys.argv[1]
    oppo_file = sys.argv[2]

    # Load the data from the CSV files
    pulled_data = pd.read_csv(pulled_file)
    oppo_data = pd.read_csv(oppo_file)

    # Filter fly balls in both datasets
    pulled_fly_balls = filter_fly_balls(pulled_data)
    oppo_fly_balls = filter_fly_balls(oppo_data)

    # Calculate required values
    total_fly_balls = len(pulled_fly_balls) + len(oppo_fly_balls)
    num_pulled_fly_balls = len(pulled_fly_balls)
    avg_distance_pulled = calculate_average_distance(pulled_fly_balls)
    num_oppo_fly_balls = len(oppo_fly_balls)
    avg_distance_oppo = calculate_average_distance(oppo_fly_balls)

    # Output the results with better labeling
    print(f"Total number of fly balls: {total_fly_balls}")
    print(f"Number of pulled fly balls: {num_pulled_fly_balls}")
    print(f"Average distance of pulled fly balls: {avg_distance_pulled:.2f} feet")
    print(f"Number of fly balls hit to the opposite field: {num_oppo_fly_balls}")
    print(f"Average distance of fly balls hit to the opposite field: {avg_distance_oppo:.2f} feet")

if __name__ == "__main__":
    main()