"""
prediction_model.py
Author: Christopher Reid
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
from collections import Counter
import matplotlib.pyplot as plt

# Define file paths
combine_agility_path = "./combine_agility_all_seasons.csv"
matched_draft_combine_path = "./matched_draft_combine_data.csv"
nba_draft_history_path = "./nba_draft_history.csv"
player_stats_path = "./player_stats.csv"
rooks_all_time_path = "./rooks_all_time.csv"

# Load datasets
combine_agility_df = pd.read_csv(combine_agility_path)
matched_combine_df = pd.read_csv(matched_draft_combine_path)
draft_history_df = pd.read_csv(nba_draft_history_path)
player_stats_df = pd.read_csv(player_stats_path)
rooks_df = pd.read_csv(rooks_all_time_path)

# Add a target column: whether the player earned a second contract
rooks_df['Second Contract'] = 1
all_players = pd.merge(player_stats_df, draft_history_df, on='Player', how='left') \
    .merge(rooks_df[['Player', 'Second Contract']], on='Player', how='left')
all_players['Second Contract'] = all_players['Second Contract'].fillna(0)  # Fill NaN for players without a second contract

# Drop rows with missing values in key features
all_players = all_players.dropna()

# Define features and target
features = all_players.drop(columns=['Player', 'Second Contract'])  # Drop non-feature columns
target = all_players['Second Contract']

# Ensure target is numeric
target = target.astype(int)

# Identify and encode categorical columns in features
categorical_cols = features.select_dtypes(include=['object']).columns
print("Categorical columns:", categorical_cols)

# Apply one-hot encoding to categorical columns
features = pd.get_dummies(features, columns=categorical_cols, drop_first=True)

# Debugging: Check transformed features
print("Transformed features shape:", features.shape)
print("First few rows of features after encoding:")
print(features.head())

# Visualize class distribution before SMOTE
def plot_class_distribution(target, title="Class Distribution Before SMOTE"):
    class_counts = Counter(target)
    plt.bar(class_counts.keys(), class_counts.values(), color=['blue', 'orange'])
    plt.title(title)
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.xticks([0, 1], ['No Second Contract', 'Second Contract'])
    plt.show()

plot_class_distribution(target)

# Handle class imbalance with conditional SMOTE
class_counts = Counter(target)
print("Class distribution before SMOTE:", class_counts)

if class_counts[0] < 2:  # If minority class has fewer than 2 samples
    print("Skipping SMOTE due to insufficient minority class samples.")
    X_resampled, y_resampled = features, target
else:
    smote = SMOTE(random_state=42, k_neighbors=min(1, class_counts[0] - 1))
    X_resampled, y_resampled = smote.fit_resample(features, target)
    print("Class distribution after SMOTE:", Counter(y_resampled))
    plot_class_distribution(y_resampled, title="Class Distribution After SMOTE")

# Split the resampled data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Train a Random Forest classifier
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}\n")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Determine feature importances
importances = model.feature_importances_
importance_df = pd.DataFrame({
    'Feature': features.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("Feature Importances:")
print(importance_df)

# Visualize top feature importances
def plot_feature_importances(importance_df, top_n=10):
    top_features = importance_df.head(top_n)
    plt.figure(figsize=(10, 6))
    plt.barh(top_features['Feature'], top_features['Importance'], color='teal')
    plt.title('Top Feature Importances')
    plt.xlabel('Importance')
    plt.gca().invert_yaxis()  # To display the most important feature on top
    plt.show()

plot_feature_importances(importance_df)