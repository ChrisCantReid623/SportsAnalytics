"""
dataMatcher.py

This script loads nba_draft_history.csv, iterates over each player, and checks against the
combined agility data from combine_agility_all_seasons.csv to find recorded data. If data
is found, it combines the information and saves it to a new CSV file. At the end, it outputs
the percentage of lottery picks that are captured in the combine agility data.

Requirements:
    - pandas (for data manipulation and CSV export)
    - nba_draft_history.csv
    - combine_agility_all_seasons.csv (consolidated combine data)

"""

import pandas as pd

# Load draft history data
draft_data = pd.read_csv("nba_draft_history.csv")

# Load combined agility data
combine_data = pd.read_csv("combine_agility_all_seasons.csv")

# Initialize a DataFrame to store matched data
matched_data = pd.DataFrame()

# Counter for matches found
total_lottery_picks = len(draft_data)
matched_lottery_picks = 0

# Loop over each draft pick in the history file
for _, draft_row in draft_data.iterrows():
    draft_year = draft_row["Draft Year"]
    player_name = draft_row["Player"]

    # Check if the player's name and draft year match in the combine data
    player_data = combine_data[(combine_data["Player Name"] == player_name) & (combine_data["Season Year"] == f"{draft_year}-{str(draft_year + 1)[-2:]}")]

    # If a match is found, add the data
    if not player_data.empty:
        combined_row = pd.concat([draft_row, player_data.iloc[0]], axis=0)
        matched_data = matched_data.append(combined_row, ignore_index=True)
        matched_lottery_picks += 1  # Increment match count
        print(f"Found data for {player_name} in season {draft_year}-{str(draft_year + 1)[-2:]}")
    else:
        print(f"No combine data found for {player_name} in draft year {draft_year}")

# Calculate the match percentage
match_percentage = (matched_lottery_picks / total_lottery_picks) * 100
print(f"\nPercentage of lottery picks captured in combine agility data: {match_percentage:.2f}%")

# Save the matched data to a new CSV file
matched_data.to_csv("matched_draft_combine_data.csv", index=False)
print("Matched data saved to matched_draft_combine_data.csv")