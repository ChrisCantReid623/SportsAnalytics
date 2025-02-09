"""
launchDistPoly.py
Homework 4: Predicting Batted Ball Distance with Polynomial Regression

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

This script performs a polynomial regression (degree 2) to predict the distance of a batted ball based on both launch speed and launch angle.
It outputs the mean squared error and the model's coefficients.

Usage:
1. Ensure the CSV file containing batted ball data (with columns: 'launch_speed', 'launch_angle', 'hit_distance_sc') is available.
2. Run the script with the CSV filename as a command-line argument.
3. If no filename is provided, 'all2024.csv' will be used as the default.
4. The script will output the mean squared error and the regression coefficients.

Example command:
$ python launchDistPoly.py all2024.csv
"""

import sys
import pandas as pd
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
    data = data[['launch_speed', 'launch_angle', 'hit_distance_sc']]

    # Drop rows with missing values
    data = data.dropna(subset=['launch_speed', 'launch_angle', 'hit_distance_sc'])

    # Extract features (launch_speed, launch_angle) and target (hit_distance_sc)
    X = data[['launch_speed', 'launch_angle']]
    y = data['hit_distance_sc']

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

    # Print coefficients
    print("\nModel Coefficients:")
    print(f"Intercept: {model.intercept_}")
    for i, coef in enumerate(model.coef_[1:], 1):  # Skip intercept
        print(f"Coefficient for Polynomial Feature {i}: {coef}")

    # Conditionally display the plot
    if display_plots:
        plt.scatter(y, y_pred, color='blue', label='Predicted vs Actual')
        plt.title('Predicted vs Actual Hit Distance (Polynomial)')
        plt.xlabel('Actual Hit Distance')
        plt.ylabel('Predicted Hit Distance')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'all2024.csv'
    main(filename)