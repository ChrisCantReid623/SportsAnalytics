import nfl_data_py as nfl
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Collect command-line inputs
yardline_start = int(sys.argv[1])
yardline_end = int(sys.argv[2])
time_remaining = int(sys.argv[3])
wp_start = float(sys.argv[4])
wp_end = float(sys.argv[5])

# Load 2023 NFL play-by-play data
pbp_data = nfl.import_pbp_data([2023])

# Filter data based on given conditions
filtered_data = pbp_data[
    (pbp_data['play_type'].isin(['run', 'pass'])) &
    (pbp_data['down'] == 1) &
    (pbp_data['yardline_100'] >= yardline_start) &
    (pbp_data['yardline_100'] <= yardline_end) &
    (pbp_data['half_seconds_remaining'] > time_remaining) &
    (pbp_data['wp'] >= wp_start) &
    (pbp_data['wp'] <= wp_end) &
    (pbp_data['two_point_attempt'] == 0)
]

# Group by team and calculate run-pass counts and EPA sums
team_stats = filtered_data.groupby('posteam').apply(
    lambda x: pd.Series({
        'pass_count': (x['play_type'] == 'pass').sum(),
        'run_count': (x['play_type'] == 'run').sum(),
        'epa_sum': x['epa'].sum()
    })
).reset_index()

# Calculate pass ratio and sort by descending order of pass ratio
team_stats['pass_ratio'] = team_stats['pass_count'] / (team_stats['pass_count'] + team_stats['run_count'])
team_stats_sorted = team_stats.sort_values(by='pass_ratio', ascending=False)

# Display each team's stats in the specified format
print("Team Stats by Highest Pass Ratio:")
for index, row in team_stats_sorted.iterrows():
    print(f"{row['posteam']} ({row['run_count']}, {row['pass_count']}) {row['pass_ratio']}")

# Scatterplot of EPA vs Pass Ratio with quadrant labels
plt.figure(figsize=(10, 6))
plt.scatter(team_stats['epa_sum'], team_stats['pass_ratio'], color='blue', label="Teams")
plt.xlabel("EPA (Expected Points Added)")
plt.ylabel("Pass Ratio")
plt.title("EPA vs Pass Ratio Scatterplot")

# Add quadrant labels based on average EPA and pass ratio
plt.axhline(y=team_stats['pass_ratio'].mean(), color='r', linestyle='--')
plt.axvline(x=team_stats['epa_sum'].mean(), color='r', linestyle='--')
plt.text(min(team_stats['epa_sum']), max(team_stats['pass_ratio']), "High EPA / High Pass Ratio", color='black')
plt.text(min(team_stats['epa_sum']), min(team_stats['pass_ratio']), "Low EPA / High Pass Ratio", color='black')
plt.text(max(team_stats['epa_sum']), max(team_stats['pass_ratio']), "High EPA / Low Pass Ratio", color='black')
plt.text(max(team_stats['epa_sum']), min(team_stats['pass_ratio']), "Low EPA / Low Pass Ratio", color='black')

# Show the plot
plt.show()