import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Step 1: Initialize an empty dictionary to store the data for each team
teams_data = defaultdict(list)

# Step 2: Read the file and parse the data
filename = 'gl2023.txt'

with open(filename, 'r') as file:
    for line in file:
        # Split each line by commas to get the fields
        fields = line.strip().split(',')

        # Extract relevant fields
        visiting_team = fields[3]
        home_team = fields[6]
        visiting_team_runs = int(fields[9])
        home_team_runs = int(fields[10])

        # Store runs scored by the visiting team and the home team
        teams_data[visiting_team].append(visiting_team_runs)
        teams_data[home_team].append(home_team_runs)

# Step 3: Calculate required statistics for each team
teams_stats = []

for team, runs in teams_data.items():
    avg_runs = np.mean(runs)
    std_dev_runs = np.std(runs)
    games_less_than_2 = sum(1 for run in runs if run < 2)
    games_less_than_3 = sum(1 for run in runs if run < 3)

    teams_stats.append((team, avg_runs, std_dev_runs, games_less_than_2, games_less_than_3))

# Step 4: Sort teams by average runs scored per game
teams_stats.sort(key=lambda x: x[1], reverse=True)

# Step 5: Print the results in the specified format
for team, avg_runs, std_dev_runs, games_less_than_2, games_less_than_3 in teams_stats:
    print(f"{team}, avg {avg_runs:.2f}, std dev {std_dev_runs:.2f}, <=2: {games_less_than_2}, <=3: {games_less_than_3}")

# Step 6: Prepare data for plotting
avg_runs_list = [x[1] for x in teams_stats]
games_less_than_2_list = [x[3] for x in teams_stats]
games_less_than_3_list = [x[4] for x in teams_stats]
std_dev_runs_list = [x[2] for x in teams_stats]
teams = [x[0] for x in teams_stats]

# Step 7: Plotting the data
plt.figure(figsize=(18, 6))

# Plot 1: Avg Runs vs Games with < 3 Runs
plt.subplot(1, 3, 1)
plt.scatter(avg_runs_list, games_less_than_3_list, color='blue', label='Data Points')
# Add trend line
z = np.polyfit(avg_runs_list, games_less_than_3_list, 1)
p = np.poly1d(z)
plt.plot(avg_runs_list, p(avg_runs_list), color='blue', linestyle='dashed', label='Trend Line')
# Calculate and display correlation coefficient
corr_coef = np.corrcoef(avg_runs_list, games_less_than_3_list)[0, 1]
plt.text(1, 1.05, f'Corr Coef: {corr_coef:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
         horizontalalignment='right')
plt.title('Avg Runs vs Games with < 3 Runs')
plt.xlabel('Average Runs Scored')
plt.ylabel('Games with < 3 Runs')
# Add team annotations
for i, team in enumerate(teams):
    plt.text(avg_runs_list[i], games_less_than_3_list[i], team, fontsize=8, ha='right')
plt.legend(loc='upper right')

# Plot 2: Avg Runs vs Games with < 2 Runs
plt.subplot(1, 3, 2)
plt.scatter(avg_runs_list, games_less_than_2_list, color='green', label='Data Points')
# Add trend line
z = np.polyfit(avg_runs_list, games_less_than_2_list, 1)
p = np.poly1d(z)
plt.plot(avg_runs_list, p(avg_runs_list), color='green', linestyle='dashed', label='Trend Line')
# Calculate and display correlation coefficient
corr_coef = np.corrcoef(avg_runs_list, games_less_than_2_list)[0, 1]
plt.text(1, 1.05, f'Corr Coef: {corr_coef:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
         horizontalalignment='right')
plt.title('Avg Runs vs Games with < 2 Runs')
plt.xlabel('Average Runs Scored')
plt.ylabel('Games with < 2 Runs')
# Add team annotations
for i, team in enumerate(teams):
    plt.text(avg_runs_list[i], games_less_than_2_list[i], team, fontsize=8, ha='right')
plt.legend(loc='upper right')

# Plot 3: Avg Runs vs Std Dev of Runs Scored
plt.subplot(1, 3, 3)
plt.scatter(avg_runs_list, std_dev_runs_list, color='red', label='Data Points')
# Add trend line
z = np.polyfit(avg_runs_list, std_dev_runs_list, 1)
p = np.poly1d(z)
plt.plot(avg_runs_list, p(avg_runs_list), color='red', linestyle='dashed', label='Trend Line')
# Calculate and display correlation coefficient
corr_coef = np.corrcoef(avg_runs_list, std_dev_runs_list)[0, 1]
plt.text(1, 1.05, f'Corr Coef: {corr_coef:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
         horizontalalignment='right')
plt.title('Avg Runs vs Std Dev of Runs Scored')
plt.xlabel('Average Runs Scored')
plt.ylabel('Standard Deviation of Runs Scored')
# Add team annotations
for i, team in enumerate(teams):
    plt.text(avg_runs_list[i], std_dev_runs_list[i], team, fontsize=8, ha='right')
plt.legend(loc='upper right')

# Show the plots
plt.tight_layout()
plt.show()
