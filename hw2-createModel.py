"""
Homework 2: Developing a win probability model

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

Description:
This script processes play-by-play baseball data to generate logistic regression models for predicting
win probabilities. The model uses game states, such as total outs, run differential, and base runner
occupancy, to predict the probability of a team winning the game at any given moment. The script
allows for separate models to be created for early innings (1-7) and late innings (8-9) to account for
differences in game dynamics over time. The logistic regression models are trained on past game data
and evaluated by predicting win probabilities for example game states from an external file,
'hw2.examples'.

Key functionalities:
- Processes play-by-play data to determine game states and likely winners.
- Splits data into early and late innings for separate model training.
- Trains logistic regression models using features such as total outs, run differential, and base occupancy.
- Displays model coefficients for each regression model.
- Predicts win probabilities for example game states using data from the 'hw2.examples' file.
- Outputs the processed play-by-play data and win probabilities into a CSV file for further analysis.

Usage:
- Input:
    - 'play_by_play.csv' containing detailed play-by-play data for multiple baseball games.
    - 'hw2.examples' containing example game states for win probability prediction.
- Output:
    - 'hw2.csv' containing the processed play-by-play data with predicted winners.

Data Source:
The data for this analysis was obtained from Sports Reference's MLB statistics.
Please cite Sports Reference when using this data:
Website: https://www.baseball-reference.com
"""

import csv


import numpy as np
from sklearn.linear_model import LogisticRegression
import pandas as pd

# Function to determine the winner of the game
def determine_winner(previous_row, first_team):
    current_team = previous_row['Team']
    return 'Away' if current_team == first_team else 'Home'

# Function to calculate total outs (up to 53 for a regulation game)
def calculate_total_outs(inning, outs):
    inning_number = int(inning[1:])
    top_of_inning = inning.startswith('t')
    return inning_number * 3 + int(outs) - (3 if top_of_inning else 0)

# Function to process base runners (1 for occupied, 0 for unoccupied)
def process_runners(runners):
    return (1 if '1' in runners else 0, 1 if '2' in runners else 0, 1 if '3' in runners else 0)

# Process the play-by-play data to generate the logistic regression model input
def process_play_by_play(play_by_play_data):
    model_data = []
    previous_row = None
    first_team = None  # Track the "Away" team
    end_of_game_count = 0  # Counter for the last play of each game

    for idx, row in enumerate(play_by_play_data):
        inning = row['Inning']
        outs = row['Outs']

        # Calculate run differential and assign likely winner based on the state of the game
        run_diff = int(row['Score'].split('-')[1]) - int(row['Score'].split('-')[0])
        likely_winner = 1 if run_diff > 0 else 0 if run_diff < 0 else None

        if inning == "t1" and (previous_row is not None and previous_row['Inning'] != "t1"):
            # This is the start of a new game; process the last play of the previous game
            winner = determine_winner(previous_row, first_team)
            end_of_game_count += 1

            # Capture the final play details for the previous game
            last_play = {
                'Total Outs': calculate_total_outs(previous_row['Inning'], previous_row['Outs']),
                'Run Diff': int(previous_row['Score'].split('-')[1]) - int(previous_row['Score'].split('-')[0]),
                '1st Base': process_runners(previous_row['Runners'])[0],
                '2nd Base': process_runners(previous_row['Runners'])[1],
                '3rd Base': process_runners(previous_row['Runners'])[2],
                'Winner': 1 if winner == 'Home' else 0,  # Override with actual game winner
            }
            model_data.append(last_play)

            # Set the new "Away" team for the upcoming game
            first_team = row['Team']

        # Process the current play and add to model data
        first_base, second_base, third_base = process_runners(row['Runners'])
        total_outs = calculate_total_outs(inning, outs)

        model_row = {
            'Total Outs': total_outs,
            'Run Diff': run_diff,
            '1st Base': first_base,
            '2nd Base': second_base,
            '3rd Base': third_base,
            'Winner': likely_winner  # Provisional likely winner
        }
        model_data.append(model_row)
        previous_row = row  # Track the previous row

    # Handle the final game in the file
    if previous_row is not None:
        winner = determine_winner(previous_row, first_team)
        last_play = {
            'Total Outs': calculate_total_outs(previous_row['Inning'], previous_row['Outs']),
            'Run Diff': int(previous_row['Score'].split('-')[1]) - int(previous_row['Score'].split('-')[0]),
            '1st Base': process_runners(previous_row['Runners'])[0],
            '2nd Base': process_runners(previous_row['Runners'])[1],
            '3rd Base': process_runners(previous_row['Runners'])[2],
            'Winner': 1 if winner == 'Home' else 0,  # Final winner
        }
        model_data.append(last_play)

    return model_data, end_of_game_count

# Split the data into early and late innings
def split_data_by_inning(model_data):
    early_innings_data = [row for row in model_data if row['Total Outs'] <= 21]
    late_innings_data = [row for row in model_data if row['Total Outs'] > 21]
    return early_innings_data, late_innings_data

# Train the logistic regression model
def train_logistic_regression(data):
    df = pd.DataFrame(data).dropna()
    X = df[['Total Outs', 'Run Diff', '1st Base', '2nd Base', '3rd Base']]
    y = df['Winner']

    if len(y.unique()) < 2:
        raise ValueError(f"Data contains only one class: {y.unique()[0]}. Cannot train the model.")

    model = LogisticRegression()
    model.fit(X, y)

    return model, X

# Display the coefficients of the logistic regression model
def display_coefficients(model, X):
    print("Logistic Regression Coefficients:")
    for feature, coef in zip(X.columns, model.coef_[0]):
        print(f"{feature}: {coef}")

# Predict win probabilities for some example game states from hw2.examples file
def predict_win_probabilities_from_file(model, examples_file, data_type):
    print(f"\nWin Probabilities for {data_type} Innings (from hw2.examples):")
    with open(examples_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            state = {k: int(v) for k, v in row.items()}
            prob = model.predict_proba([list(state.values())])[0][1]
            print(f"Predicted win probability for state {state}: {prob:.2f}")

# Main function to create model data and perform logistic regression
def create_model_data(input_file, output_file, examples_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        play_by_play_data = list(reader)

    # Process play-by-play data
    model_data, end_of_game_count = process_play_by_play(play_by_play_data)

    # Split data into early innings and late innings
    early_innings_data, late_innings_data = split_data_by_inning(model_data)

    # Train logistic regression models for unsplit and split datasets
    original_model, original_X = train_logistic_regression(model_data)
    early_model, early_X = train_logistic_regression(early_innings_data)
    late_model, late_X = train_logistic_regression(late_innings_data)

    # Display the coefficients of the original and split models
    print("Logistic Regression for Unsplit (Full) Data:")
    display_coefficients(original_model, original_X)

    print("\nLogistic Regression for Early Innings (1-7):")
    display_coefficients(early_model, early_X)

    print("\nLogistic Regression for Late Innings (8-9):")
    display_coefficients(late_model, late_X)

    # Predict win probabilities for example game states from the examples file
    predict_win_probabilities_from_file(original_model, examples_file, "Unsplit")
    predict_win_probabilities_from_file(early_model, examples_file, "Early")
    predict_win_probabilities_from_file(late_model, examples_file, "Late")

    # Write the model data to a CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['Total Outs', 'Run Diff', '1st Base', '2nd Base', '3rd Base', 'Winner']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in model_data:
            writer.writerow(row)

    print(f"Total number of games processed: {end_of_game_count}")

# Example usage:
input_csv = 'play_by_play.csv'
output_csv = 'hw2.csv'
examples_csv = 'hw2.examples'
create_model_data(input_csv, output_csv, examples_csv)
