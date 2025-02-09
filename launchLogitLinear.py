"""
launchLogitLinear.py
Homework 4: Predicting Home Runs with Logistic Regression (Linear)

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script performs a logistic regression to predict whether a batted ball results in a home run
based on the launch angle and launch speed. The regression is linear in nature, and the script
outputs the mean squared error and the model's coefficients, one per line.

Additionally, the script generates two plots:
1. A scatter plot of launch speed vs. launch angle, colored by whether the batted ball is a home run.
2. A decision boundary plot to visualize the logistic regression model's classification.

Usage:
1. Ensure the CSV file containing batted ball data (with columns: 'launch_speed', 'launch_angle', 'events') is available.
2. Run the script with the CSV filename as a command-line argument.
3. If no filename is provided, 'all2024.csv' will be used as the default.
4. The script will output the mean squared error, the regression coefficients, and optionally generate the plots.

Example command:
$ python launchLogitLinear.py all2024.csv
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
from matplotlib.colors import ListedColormap

# Setting to False disables plots
display_plots = False

def plot_decision_boundary(X, y, model):
    # Define range for the grid
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    # Predict class for every point in the grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Create contour plot
    plt.contourf(xx, yy, Z, alpha=0.8, cmap=ListedColormap(('red', 'blue')))
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', marker='o', cmap=ListedColormap(('red', 'blue')))
    plt.xlabel('Launch Speed')
    plt.ylabel('Launch Angle')
    plt.title('Decision Boundary and Data Points')
    plt.show()

def main(filename='all2024.csv'):
    # Print the filename being processed
    print(f"Processing file: {filename}")

    # Load the data
    data = pd.read_csv(filename)

    # Filter data to extract relevant columns
    data = data[['launch_speed', 'launch_angle', 'events']]

    # Drop rows with missing values in 'launch_speed' or 'launch_angle'
    data = data.dropna(subset=['launch_speed', 'launch_angle'])

    # Convert the 'events' column to a binary target: 1 for 'home_run', 0 otherwise
    data['result'] = data['events'].apply(lambda x: 1 if x == 'home_run' else 0)

    # Extract features and target
    X = data[['launch_speed', 'launch_angle']].values  # Use launch speed and launch angle as features
    y = data['result'].values  # Target (whether the batted ball is a home run)

    # Initialize and fit the logistic regression model
    model = LogisticRegression()
    model.fit(X, y)

    # Predict the target using the model
    y_pred = model.predict(X)

    # Calculate mean squared error
    mse = mean_squared_error(y, y_pred)

    # Print labeled outputs
    print("Mean Squared Error:")
    print(mse)

    print("\nCoefficients:")
    for coef in model.coef_[0]:
        print(coef)

    # Conditionally display the plots based on the toggle
    if display_plots:
        # Plot 1: Scatter plot of launch speed vs launch angle
        plt.figure()
        plt.scatter(data['launch_speed'], data['launch_angle'], c=data['result'], cmap=ListedColormap(['red', 'blue']), edgecolors='k')
        plt.title('Launch Speed vs Launch Angle (Red: Not Home Run, Blue: Home Run)')
        plt.xlabel('Launch Speed')
        plt.ylabel('Launch Angle')
        plt.show()

        # Plot 2: Decision boundary plot
        plot_decision_boundary(X, y, model)

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'all2024.csv'
    main(filename)