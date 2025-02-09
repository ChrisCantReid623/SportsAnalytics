import pandas as pd
from scipy.stats import linregress
import random

# Load the CSV file into a pandas DataFrame
file_path = "teamData2023.csv"  # Ensure the file path is correct
data = pd.read_csv(file_path)

# Display the first few rows of the dataset to verify loading
print(data.head())

# Extract the independent variable (Hits 'H') and dependent variable (Runs 'R') for all teams
hits = data['H']
runs = data['R']

# Perform linear regression on the entire dataset
slope, intercept, r_value, p_value, std_err = linregress(hits, runs)

# Calculate R-squared value
r_squared = r_value ** 2

# Print the regression results for the entire dataset
print("Linear Regression Model for All Teams:")
print(f"Slope: {slope}")
print(f"Intercept: {intercept}")
print(f"R-squared: {r_squared}")
print(f"P-value: {p_value}")
print(f"Standard Error: {std_err}\n")

# Randomly select two distinct teams
team_indices = random.sample(range(len(data)), 2)
team1 = data.iloc[team_indices[0]]
team2 = data.iloc[team_indices[1]]

# Get the actual hits and runs for the two randomly selected teams
team1_name = team1['Tm']
team1_hits = team1['H']
team1_actual_runs = team1['R']

team2_name = team2['Tm']
team2_hits = team2['H']
team2_actual_runs = team2['R']

# Predict runs for the two teams using the regression model
team1_predicted_runs = slope * team1_hits + intercept
team2_predicted_runs = slope * team2_hits + intercept

# Print actual vs. predicted runs for the two randomly selected teams
print("Testing Regression on Two Randomly Selected Teams:")
print(f"{team1_name} - Actual Runs: {team1_actual_runs}, Predicted Runs: {team1_predicted_runs:.2f}")
print(f"{team2_name} - Actual Runs: {team2_actual_runs}, Predicted Runs: {team2_predicted_runs:.2f}")
