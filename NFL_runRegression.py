# NFL_runRegression_manual.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats


# Function to calculate standard errors, t-values, and p-values
def regression_diagnostics(X, y, model):
    n = len(y)  # Number of observations
    p = X.shape[1]  # Number of predictors (including intercept)

    # Make predictions
    y_pred = model.predict(X)

    # Calculate residuals
    residuals = y - y_pred

    # Estimate variance of the residuals
    residual_sum_of_squares = np.sum(residuals ** 2)
    sigma_squared = residual_sum_of_squares / (n - p)

    # Calculate the variance-covariance matrix
    X_with_intercept = np.hstack([np.ones((X.shape[0], 1)), X])  # Add intercept
    cov_matrix = sigma_squared * np.linalg.inv(X_with_intercept.T @ X_with_intercept)

    # Standard errors of the coefficients
    std_err = np.sqrt(np.diag(cov_matrix))

    # Coefficients (intercept + predictors)
    coefficients = np.insert(model.coef_, 0, model.intercept_)  # Add intercept to coefficients

    # Calculate t-values and p-values
    t_values = coefficients / std_err
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_values), df=n - p))

    return coefficients, std_err, t_values, p_values


# Read in the data from the CSV file
data = pd.read_csv('NFLdata21-23.csv')

# Define the target variable (Margin)
y = data['Margin']  # Target variable (net point differential)

# --- FULL MODEL ---
X_full = data[['PY_A', 'RY_A', 'DPY_A', 'DRY_A', 'PENDIF', 'RETTD', 'TO', 'DTO']]  # Offense and defense stats
X_train_full, X_test_full, y_train_full, y_test_full = train_test_split(X_full, y, test_size=0.2, random_state=42)

model_full = LinearRegression()
model_full.fit(X_train_full, y_train_full)

# Perform diagnostics for the full model
coefficients_full, std_err_full, t_values_full, p_values_full = regression_diagnostics(X_train_full, y_train_full,
                                                                                       model_full)

# Output for full model
print("\n--- Full Model Regression Diagnostics ---")
variables_full = ['Intercept', 'PY_A (Pass Y/A)', 'RY_A (Run Y/A)', 'DPY_A (Def Pass Y/A)', 'DRY_A (Def Run Y/A)',
                  'PENDIF (Penalty Differential)', 'RETTD (Return TD Differential)', 'TO (Turnovers)',
                  'DTO (Def Turnovers)']
print(f"{'Variable':<30}{'Coefficient':>12}{'Std Err':>12}{'t-value':>12}{'p-value':>12}")
for var, coef, se, t_val, p_val in zip(variables_full, coefficients_full, std_err_full, t_values_full, p_values_full):
    print(f"{var:<30}{coef:>12.4f}{se:>12.4f}{t_val:>12.4f}{p_val:>12.4f}")

# --- RUN STATS ONLY ---
X_run = data[['RY_A', 'DRY_A']]
X_train_run, X_test_run, y_train_run, y_test_run = train_test_split(X_run, y, test_size=0.2, random_state=42)

model_run = LinearRegression()
model_run.fit(X_train_run, y_train_run)

# Perform diagnostics for the run stats model
coefficients_run, std_err_run, t_values_run, p_values_run = regression_diagnostics(X_train_run, y_train_run, model_run)

# Output for run stats model
print("\n--- Run Stats Model Regression Diagnostics (RY_A, DRY_A) ---")
variables_run = ['Intercept', 'RY_A (Run Y/A)', 'DRY_A (Def Run Y/A)']
print(f"{'Variable':<30}{'Coefficient':>12}{'Std Err':>12}{'t-value':>12}{'p-value':>12}")
for var, coef, se, t_val, p_val in zip(variables_run, coefficients_run, std_err_run, t_values_run, p_values_run):
    print(f"{var:<30}{coef:>12.4f}{se:>12.4f}{t_val:>12.4f}{p_val:>12.4f}")

# --- PASS STATS ONLY (PY_A and DPY_A) ---
X_pass = data[['PY_A', 'DPY_A']]
X_train_pass, X_test_pass, y_train_pass, y_test_pass = train_test_split(X_pass, y, test_size=0.2, random_state=42)

model_pass = LinearRegression()
model_pass.fit(X_train_pass, y_train_pass)

# Perform diagnostics for the pass stats model
coefficients_pass, std_err_pass, t_values_pass, p_values_pass = regression_diagnostics(X_train_pass, y_train_pass,
                                                                                       model_pass)

# Output for pass stats model
print("\n--- Pass Stats Model Regression Diagnostics (PY_A, DPY_A) ---")
variables_pass = ['Intercept', 'PY_A (Pass Y/A)', 'DPY_A (Def Pass Y/A)']
print(f"{'Variable':<30}{'Coefficient':>12}{'Std Err':>12}{'t-value':>12}{'p-value':>12}")
for var, coef, se, t_val, p_val in zip(variables_pass, coefficients_pass, std_err_pass, t_values_pass, p_values_pass):
    print(f"{var:<30}{coef:>12.4f}{se:>12.4f}{t_val:>12.4f}{p_val:>12.4f}")