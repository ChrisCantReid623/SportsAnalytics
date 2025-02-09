"""
rookieSuccess_athletic.py: Analyzing the relationship between athletic metrics and rookie contract success
Author: Christopher Reid
Purpose: This script combines data on rookie contracts, player stats, and athletic combine performance
         to predict the likelihood of earning a second contract.

Supporting Data files:
    - combine_agility_all_seasons.csv
    - matched_draft_combine_data.csv
    - nba_draft_history.csv
    - player_stats.csv
    - rooks_all_time.csv
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Define relative file paths based on the current script directory
base_dir = os.path.dirname(__file__)
player_stats_path = os.path.join(base_dir, "player_stats.csv")
rookie_contracts_path = os.path.join(base_dir, "rooks_all_time.csv")
combine_agility_path = os.path.join(base_dir, "combine_agility_all_seasons.csv")

# Load the datasets
print("Loading datasets...")
player_stats = pd.read_csv(player_stats_path)
rookie_contracts = pd.read_csv(rookie_contracts_path)
combine_agility = pd.read_csv(combine_agility_path)

# Clean up the `Value` column in rookie_contracts
print("Cleaning contract values...")
rookie_contracts['Value'] = (
    rookie_contracts['Value']
    .replace(r'[\$,]', '', regex=True)
    .astype(float)
)

# Merge player stats and rookie contracts on "Player"
print("Combining player stats with rookie contracts...")
threshold = 5000000  # Threshold for significant contracts
print(f"Using contract value threshold: ${threshold}")
player_stats = pd.merge(player_stats, rookie_contracts[['Player', 'Value']], on="Player", how="left")
player_stats['Value'] = player_stats['Value'].fillna(0)
player_stats['Earned_Second_Contract'] = (player_stats['Value'] > threshold).astype(int)

# Check class distribution
print("Class distribution for Earned_Second_Contract:")
print(player_stats['Earned_Second_Contract'].value_counts())

# Handle duplicates in combine_agility
print("Handling duplicates in combine_agility...")
combine_agility = combine_agility.groupby("Player", as_index=False).mean()

# Add athletic metrics to player stats
athletic_columns = [
    "Lane Agility", "Shuttle Run", "Three Quarter Sprint",
    "Standing Vertical", "Max Vertical", "Bench Press"
]
missing_columns = [col for col in athletic_columns if col not in combine_agility.columns]
if missing_columns:
    print(f"Missing columns in combine_agility: {missing_columns}")
else:
    print("All athletic columns present in combine_agility.")

print("Adding athletic metrics...")
for column in athletic_columns:
    if column in combine_agility.columns:
        player_stats[column] = player_stats['Player'].map(
            combine_agility.set_index('Player Name')[column]
        )
    else:
        print(f"Skipping missing column: {column}")

# Features for the model
features = [
    "Seasons Played", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
    "2P", "2PA", "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST",
    "STL", "BLK", "TOV", "PF", "PTS"
] + [col for col in athletic_columns if col in player_stats.columns]

# Ensure all features are numeric
print("Converting features to numeric...")
player_stats[features] = player_stats[features].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing or invalid data in the features
print("Dropping rows with missing values in features...")
player_stats = player_stats.dropna(subset=features)

# Separate features and target
X = player_stats[features]
y = player_stats['Earned_Second_Contract']

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Address class imbalance
print("Balancing the dataset...")
try:
    smote = SMOTE(random_state=42, k_neighbors=1)  # Adjust k_neighbors to avoid errors
    X_balanced, y_balanced = smote.fit_resample(X_scaled, y)
except ValueError:
    print("SMOTE failed due to extreme imbalance. Using duplication instead.")
    minority_class = player_stats[player_stats['Earned_Second_Contract'] == 0]
    majority_class = player_stats[player_stats['Earned_Second_Contract'] == 1]
    minority_duplicated = pd.concat([minority_class] * (len(majority_class) // len(minority_class)), ignore_index=True)
    balanced_data = pd.concat([majority_class, minority_duplicated], ignore_index=True)
    X_balanced = balanced_data[features]
    y_balanced = balanced_data['Earned_Second_Contract']

# Train-test split
print("Splitting data into training and testing sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced, test_size=0.2, random_state=42
)

# Build logistic regression model
print("Training logistic regression model...")
logistic_model = LogisticRegression(random_state=42, max_iter=1000)
logistic_model.fit(X_train, y_train)

# Predictions and evaluation
y_pred = logistic_model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Cross-validation
print("\nPerforming stratified cross-validation...")
cross_val_scores = cross_val_score(logistic_model, X_balanced, y_balanced, cv=5, scoring='accuracy')
print(f"Cross-Validation Accuracy: {cross_val_scores.mean():.2f} ± {cross_val_scores.std():.2f}")

# Feature importance
importance = logistic_model.coef_[0]
feature_importance = pd.DataFrame({
    "Feature": features,
    "Importance": importance
}).sort_values(by="Importance", ascending=False)

print("\nFeature Importance:")
print(feature_importance)