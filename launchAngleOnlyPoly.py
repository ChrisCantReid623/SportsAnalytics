"""
launchAngleOnlyPoly.py
Homework 4: Predicting Batted Ball Distance with Polynomial Regression (Launch Angle Only)

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script performs a polynomial regression (degree 2 by default) to predict the distance of a batted ball
based on launch angle only. It outputs the mean squared error and the model's coefficients.

Additionally, the script generates a plot of launch angle vs. hit distance with a regression curve.

Usage:
1. Ensure the CSV file containing batted ball data (with columns: 'launch_angle', 'hit_distance_sc') is available.
2. Run the script with the CSV filename as a command-line argument.
3. If no filename is provided, 'all2024.csv' will be used as the default.
4. The script will output the mean squared error, the regression coefficients, and optionally display the plot.

Example command:
$ python launchAngleOnlyPoly.py all2024.csv
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error

# Setting to False disables plots
display_plots = False

def main(filename='all2024.csv'):
    # Print the filename being processed
    print(f"Processing file: {filename}")

    # Load the data
    data = pd.read_csv(filename)

    # Filter data to extract relevant columns
    data = data[['launch_angle', 'hit_distance_sc']]

    # Drop rows with missing values in 'launch_angle' or 'hit_distance_sc'
    data = data.dropna(subset=['launch_angle', 'hit_distance_sc'])

    # Extract features (launch_angle) and target (hit_distance_sc)
    X = data[['launch_angle']]  # Use launch angle as the only feature
    y = data['hit_distance_sc']  # Target (hit distance)

    # Generate polynomial features (degree 2)
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)

    # Initialize and fit the polynomial regression model
    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict the target using the model
    y_pred = model.predict(X_poly)

    # Calculate mean squared error
    mse = mean_squared_error(y, y_pred)

    # Print labeled outputs
    print("Mean Squared Error:")
    print(mse)

    # Print better labeled coefficients
    print("\nModel Coefficients:")
    print(f"Intercept: {model.intercept_}")
    print(f"Coefficient for Linear Term (launch_angle): {model.coef_[1]}")
    print(f"Coefficient for Quadratic Term (launch_angle^2): {model.coef_[2]}")

    # Conditionally display the plot
    if display_plots:
        plt.scatter(X, y, color='blue', label='Actual data')

        # Sort X and y_pred for a smooth curve
        X_sorted = np.sort(X, axis=0)
        y_pred_sorted = model.predict(poly.fit_transform(X_sorted))

        plt.plot(X_sorted, y_pred_sorted, color='red', label='Polynomial regression curve')
        plt.title('Launch Angle vs Hit Distance (Polynomial)')
        plt.xlabel('Launch Angle')
        plt.ylabel('Hit Distance')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'all2024.csv'
    main(filename)