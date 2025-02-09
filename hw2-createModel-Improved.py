"""
Homework 2: Developing a win probability model (Improved Model)

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

Description:
This script processes play-by-play baseball data to generate improved logistic regression models for
predicting win probabilities. The model is improved by splitting the data into early innings (1-7) and late
innings (8-9), accounting for differences in game dynamics over time. Separate logistic regression models
are trained for each inning group to provide more accurate predictions in different stages of the game.

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


# Function to calculate total outs
def calculate_total_outs(inning, outs):
    inning_number = int(inning[1:])
    top_of_inning = inning.startswith('t')
    return inning_number * 3 + int(outs) - (3 if top_of_inning else 0)


# Function to process base runners (1 for occupied, 0 for unoccupied)
def process_runners(runners):
    return (1 if '1' in runners else 0, 1 if '2' in runners else 0, 1 if '3' in runners else 0)


# Function to determine the winner of the game
def determine_winner(previous_row, first_team):
    current_team = previous_row['Team']
    return 'Away' if current_team == first_team else 'Home'


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


# Split the data into early and late innings based on the outs
def split_inning_data(model_data):
    early_innings_data = [row for row in model_data if row['Total Outs'] <= 21]
    late_innings_data = [row for row in model_data if row['Total Outs'] > 21]
    return early_innings_data, late_innings_data


# Train the logistic regression model
def train_logistic_regression(data, inning_type):
    if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
        print(f"Error: Data passed to {inning_type} is not in the correct format.")
        return None, None

    # Remove any rows where 'Winner' is None
    cleaned_data = [row for row in data if row['Winner'] is not None]

    if not cleaned_data:
        print(f"Error: No valid data available for {inning_type}.")
        return None, None

    print(
        f"Training logistic regression for {inning_type}. Data sample: {cleaned_data[:1]}")  # Print the first data row for debugging

    df = pd.DataFrame(cleaned_data).dropna()
    X = df[['Total Outs', 'Run Diff', '1st Base', '2nd Base', '3rd Base']]
    y = df['Winner']

    if len(y.unique()) < 2:
        print(f"Error: Only one class found in the data for {inning_type}. Cannot train the model.")
        return None, None

    model = LogisticRegression()
    model.fit(X, y)
    return model, X


# Display the coefficients of the logistic regression model
def display_coefficients(model, X, inning_type):
    if model is None:
        print(f"Error: Model for {inning_type} could not be trained.")
        return
    print(f"Logistic Regression Coefficients for {inning_type}:")
    for feature, coef in zip(X.columns, model.coef_[0]):
        print(f"{feature}: {coef}")


# Predict win probabilities from the hw2.examples file using correct model based on inning
def predict_from_examples(early_model, late_model, examples_file):
    print("\nWin Probabilities for examples from hw2.examples:")
    with open(examples_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            state = {k: int(v) for k, v in row.items()}
            if state['Total Outs'] <= 21:
                if early_model:
                    prob = early_model.predict_proba([list(state.values())])[0][1]
                    print(f"Predicted win probability for early state {state}: {prob:.2f}")
            else:
                if late_model:
                    prob = late_model.predict_proba([list(state.values())])[0][1]
                    print(f"Predicted win probability for late state {state}: {prob:.2f}")


# Main function to create the improved model data and perform logistic regression
def create_improved_model(input_file, examples_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        play_by_play_data = list(reader)

    # Process the play-by-play data
    model_data, _ = process_play_by_play(play_by_play_data)

    # Split the data into early and late innings
    early_innings_data, late_innings_data = split_inning_data(model_data)

    # Train logistic regression models for early and late innings
    early_model, early_X = train_logistic_regression(early_innings_data, "Innings 1-7")
    late_model, late_X = train_logistic_regression(late_innings_data, "Innings 8-9")

    # Display the coefficients of the early and late inning models
    display_coefficients(early_model, early_X, "Innings 1-7")
    display_coefficients(late_model, late_X, "Innings 8-9")

    # Predict win probabilities for examples using the correct models
    predict_from_examples(early_model, late_model, examples_file)


# Example usage:
input_csv = 'play_by_play.csv'
examples_csv = 'hw2.examples'
create_improved_model(input_csv, examples_csv)
