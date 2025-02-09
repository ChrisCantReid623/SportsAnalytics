"""
rookieSuccess_stratifiedCV.py: Addressing class imbalance using stratified cross-validation
Author: Christopher Reid
Purpose: This script analyzes factors predicting whether a rookie earns a second contract,
         using stratified cross-validation to handle class imbalance and evaluating the model's performance.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import numpy as np
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
merged_data['Value'] = merged_data['Value'].fillna(0)
merged_data['Earned_Second_Contract'] = (merged_data['Value'] > 1000000).astype(int)

# Check class distribution
print("\nClass Distribution in Earned_Second_Contract:")
print(merged_data['Earned_Second_Contract'].value_counts())

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
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Logistic regression with class weights
logistic_model = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')

# Stratified cross-validation
print("\nPerforming stratified cross-validation...")
stratified_kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(logistic_model, X_scaled, y, cv=stratified_kfold, scoring='accuracy')

print(f"\nCross-Validation Accuracy: {np.mean(cv_scores):.2f} ± {np.std(cv_scores):.2f}")

# Train logistic regression model on training data
logistic_model.fit(X_train, y_train)

# Predictions and evaluation
y_pred = logistic_model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
importance = logistic_model.coef_[0]
feature_importance = pd.DataFrame({
    "Feature": features,
    "Importance": importance
}).sort_values(by="Importance", ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Generate and plot ROC curve
print("\nGenerating ROC Curve...")
y_prob = logistic_model.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_prob)
fpr, tpr, thresholds = roc_curve(y_test, y_prob)

plt.figure()
plt.plot(fpr, tpr, label=f"Logistic Regression (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.show()