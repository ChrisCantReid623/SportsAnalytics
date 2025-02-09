import pandas as pd
import numpy as np

# Load the CSV file into a pandas DataFrame
file_path = "teamData2023.csv"  # Ensure the file path is correct
data = pd.read_csv(file_path)

# Print the available columns to ensure we're using the correct ones
print(data.columns)

# Calculate first base hits (singles) and add it as a new column '1B'
data['1B'] = data['H'] - data['2B'] - data['3B'] - data['HR']

# Define the independent variables, including singles ('1B')
independent_vars = ['1B', '2B', '3B', 'HR', 'BB', 'HBP', 'SB', 'CS']

# Extract the independent variables (X) and the dependent variable (y)
X = data[independent_vars]
y = data['R']

# Add a column of ones to X for the intercept term (bias)
X = np.column_stack([np.ones(X.shape[0]), X])

# Perform the normal equation to compute the coefficients
# beta = (X^T X)^(-1) X^T y
beta = np.linalg.inv(X.T @ X) @ X.T @ y

# Print the coefficients
print("Multiple Regression Model Coefficients:")
for var, coef in zip(['Intercept'] + independent_vars, beta):
    print(f"{var}: {coef:.4f}")

# Predict the runs using the model
y_pred = X @ beta

# Calculate R-squared
ss_total = np.sum((y - np.mean(y)) ** 2)
ss_residual = np.sum((y - y_pred) ** 2)
r_squared = 1 - (ss_residual / ss_total)

print(f"\nR-squared: {r_squared:.4f}")

# Estimate the effect of home runs based on assumptions
# Average 38 batters per game, 4.8 runs per game, and 13 baserunners
# Assume a home run clears the bases, on average
average_baserunners = 13
runs_per_game = 4.8
batter_count = 38

# Estimate how home runs could affect runs per game
# Assume HR clears the bases and each HR generates roughly 1.5 to 3 runs
hr_coefficient_estimate = average_baserunners / batter_count * runs_per_game
print(f"\nEstimated coefficient for home runs (simple arithmetic): {hr_coefficient_estimate:.2f}")
