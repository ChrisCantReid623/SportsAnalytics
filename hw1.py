"""
Homework 1: MLB Offensive Statistics Correlation Analysis

Author: Christopher Reid
Course: 496 Sports Analytics, Fall 2024

Description:
This program analyzes the correlation between MLB offensive statistics and runs scored (R/G) for a given season.
It performs linear regression on various offensive metrics such as Hits (H), Batting Average (BA), On-base Percentage (OBP),
Slugging Percentage (SLG), On-base Plus Slugging (OPS), and Adjusted On-base Plus Slugging (OPS+), calculating the
correlation coefficient (R²) for each metric. The output includes plots of each regression with points and lines
alongside the R² value.

Usage:
- Change the 'season_year' variable to the desired season (e.g., '1982', '1911') to load the appropriate dataset.
- The CSV files should be named in the format 'MLB_<season_year>.csv' and located in the same directory as this script.

Data Source:
The data for this analysis was obtained from Sports Reference's MLB statistics.
Please cite Sports Reference when using this data:
Website: https://www.baseball-reference.com

Example citation:
"Data provided by Sports Reference. Visit https://www.baseball-reference.com/ for more details."

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Define the function to perform linear regression and return the correlation coefficient
def calculate_correlation_from_file(filename):
    # Load the dataset
    data = pd.read_csv(filename)

    # Define the independent variables and the dependent variable
    independent_vars = {
        'H': 'Hits',
        'BA': 'Batting Average',
        'OBP': 'On-base Percentage',
        'SLG': 'Slugging Percentage',
        'OPS': 'On-base Plus Slugging',
        'OPS+': 'Adjusted On-base Plus Slugging'
    }

    dependent_var = 'R/G'  # Runs per Game

    # Initialize a dictionary to store the correlation coefficients
    correlations = {}

    # Prepare the plot - 2 rows, 3 columns (to accommodate all 5 plots + 1 empty spot)
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 12))
    fig.suptitle(f'Correlation Plots for {filename}')

    # Perform linear regression for each independent variable
    for idx, (ind_var, label) in enumerate(independent_vars.items()):
        X = data[ind_var].values.reshape(-1, 1)
        y = data[dependent_var].values

        # Create the linear regression model and fit it
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)

        # Calculate the correlation coefficient (R^2)
        r2 = r2_score(y, y_pred)
        correlations[label] = r2

        # Plot the data and the regression line
        ax = axes[idx // 3, idx % 3]
        ax.scatter(X, y, color='blue')
        ax.plot(X, y_pred, color='red')
        ax.set_title(f'R/G vs {label} (R² = {r2:.2f})')
        ax.set_xlabel(label)
        ax.set_ylabel('R/G')

    # Remove the last empty subplot if there are fewer than 6 plots
    if len(independent_vars) < 6:
        fig.delaxes(axes[1, 2])

    # Adjust layout and save the plot
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plot_filename = f"correlation_plots_{filename.split('/')[-1].split('.')[0]}.png"
    plt.savefig(plot_filename)

    # Output the correlation coefficients
    for label, r2 in correlations.items():
        print(f'Correlation coefficient for R/G vs {label}: {r2}')

    # Display the plot
    plt.show()

# CSV File Selection:
season_year = '2023'

csv_filename = f'MLB_{season_year}.csv'
calculate_correlation_from_file(csv_filename)
