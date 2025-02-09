"""
rookieSuccess.py: Analyzing factors that predict whether a rookie earns a second contract
Author: Christopher Reid
Purpose: This script merges college player stats with rookie contract extension data,
         builds logistic regression models to predict the likelihood of earning a second contract,
         and identifies features that contribute most to predictive success.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE
import matplotlib.pyplot as plt

# Define relative file paths based on the current script directory
base_dir = os.path.dirname(__file__)
player_stats_path = os.path.join(base_dir, "player_stats.csv")
rookie_contracts_path = os.path.join(base_dir, "rooks_all_time.csv")

# Load the datasets
print("Loading datasets...")
player_stats = pd.read_csv(player_stats_path)
rookie_contracts = pd.read_csv(rookie_contracts_path)

# Clean up the `Value` column in rookie_contracts
print("Cleaning contract values...")
rookie_contracts['Value'] = (
    rookie_contracts['Value']
    .replace(r'[\$,]', '', regex=True)
    .astype(float)
)

# Merge datasets on Player name
print("Merging datasets...")
merged_data = pd.merge(player_stats, rookie_contracts, on="Player", how="outer")  # Use outer join to include unmatched players

# Fill missing `Value` with 0 for players without a recorded contract value
merged_data['Value'] = merged_data['Value'].fillna(0)

# Add target variable: Did the player earn a significant second contract? (1 = Yes, 0 = No)
merged_data['Earned_Second_Contract'] = (merged_data['Value'] > 1000000).astype(int)

# Check class distribution
print("\nClass Distribution in Earned_Second_Contract:")
print(merged_data['Earned_Second_Contract'].value_counts())

# Ensure there are samples from both classes
if merged_data['Earned_Second_Contract'].nunique() < 2:
    raise ValueError("The dataset must include samples from both classes (0 and 1).")

# Features for the model
features = [
    "Seasons Played", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA",
    "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
]

# Drop rows with missing data in features
merged_data = merged_data.dropna(subset=features)

X = merged_data[features]
y = merged_data['Earned_Second_Contract']

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

# Build logistic regression model
print("\nTraining logistic regression model...")
logistic_model = LogisticRegression(random_state=42, max_iter=1000)
logistic_model.fit(X_train, y_train)

# Predictions and evaluation
y_pred = logistic_model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Cross-validation
cv_scores = cross_val_score(logistic_model, X_scaled, y, cv=5, scoring='accuracy')
print(f"\nCross-Validation Accuracy: {np.mean(cv_scores):.2f} ± {np.std(cv_scores):.2f}")

# Feature importance
importance = logistic_model.coef_[0]
feature_importance = pd.DataFrame({
    "Feature": features,
    "Importance": importance
}).sort_values(by="Importance", ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Recursive Feature Elimination (RFE)
print("\nPerforming Recursive Feature Elimination (RFE)...")
rfe = RFE(logistic_model, n_features_to_select=10)
rfe.fit(X_train, y_train)
selected_features = [features[i] for i in range(len(features)) if rfe.support_[i]]
print(f"Top 10 Features: {selected_features}")

# ROC Curve and AUC
print("\nGenerating ROC Curve...")
y_prob = logistic_model.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f"ROC Curve (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.grid()
plt.show()