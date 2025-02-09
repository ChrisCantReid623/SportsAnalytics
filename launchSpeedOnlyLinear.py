"""
launchSpeedOnlyLinear.py
Homework 4: Predicting Batted Ball Distance with Linear Regression (Launch Speed Only)

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script performs a linear regression to predict the distance of a batted ball based on launch speed only.
It outputs the mean squared error and the model's coefficients.

Additionally, the script generates a plot of launch speed vs. hit distance with a regression line.

Usage:
1. Ensure the CSV file containing batted ball data (with columns: 'launch_speed', 'hit_distance_sc') is available.
2. Run the script with the CSV filename as a command-line argument.
3. If no filename is provided, 'all2024.csv' will be used as the default.
4. The script will output the mean squared error, the regression coefficients, and optionally display the plot.

Example command:
$ python launchSpeedOnlyLinear.py all2024.csv
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Setting to False disables plots
display_plots = False

def main(filename='all2024.csv'):
    # Print the filename being processed
    print(f"Processing file: {filename}")

    # Load the data
    data = pd.read_csv(filename)
    # Filter data to extract relevant columns
    data = data[['launch_speed', 'hit_distance_sc']]

    # Drop rows with missing values in 'launch_speed' or 'hit_distance_sc'
    data = data.dropna(subset=['launch_speed', 'hit_distance_sc'])

    # Extract features (launch_speed) and target (hit_distance_sc)
    X = data[['launch_speed']]  # Use launch speed as the only feature
    y = data['hit_distance_sc']  # Target (hit distance)

    # Initialize and fit the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the target using the model
    y_pred = model.predict(X)

    # Calculate mean squared error
    mse = mean_squared_error(y, y_pred)

    # Print labeled outputs
    print("Mean Squared Error:")
    print(mse)

    print("\nCoefficients:")
    print(model.coef_[0])

    # Conditionally display the plot
    if display_plots:
        plt.scatter(X, y, color='blue', label='Actual data')
        plt.plot(X, y_pred, color='red', label='Regression line')
        plt.title('Launch Speed vs Hit Distance')
        plt.xlabel('Launch Speed')
        plt.ylabel('Hit Distance')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'all2024.csv'
    main(filename)