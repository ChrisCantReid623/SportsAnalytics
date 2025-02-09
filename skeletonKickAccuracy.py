import nfl_data_py as nfl
from collections import defaultdict
import math

# Create a defaultdict for field goal success rates, indexed by distance range
fgDict = defaultdict(lambda: (0, 0))

# Import play-by-play data for multiple years
years = [2021, 2022, 2023]  # Adjust the range according to your dataset
pbp = nfl.import_pbp_data(years, downcast=True, cache=False, alt_path=None)

# Iterate through every play to find field goal attempts and track success rates by distance range
for index, row in pbp.iterrows():
    playType = row.get("play_type", None)
    if playType != "field_goal":  # Only consider field goals
        continue

    distance = row.get("kick_distance", None)
    result = row.get("field_goal_result", None)

    # Ensure valid distance and result data
    if distance is None or math.isnan(distance) or result not in ["made", "missed"]:
        continue

    # Convert distance to integer and filter reasonable range (e.g., 20-60 yards)
    distance = int(distance)
    if distance < 20 or distance > 60:
        continue

    # Group by 5-yard distance increments (e.g., 20-24, 25-29, etc.)
    distance_group = (distance // 5) * 5
    oldTuple = fgDict[distance_group]

    if result == "made":
        fgDict[distance_group] = (oldTuple[0] + 1, oldTuple[1] + 1)
    else:
        fgDict[distance_group] = (oldTuple[0] + 1, oldTuple[1])

# Output the results for each distance group
print("Field Goal Accuracy by Distance Range")
for distance_group, (attempts, makes) in sorted(fgDict.items()):
    if attempts > 0:  # Only display ranges with attempts
        accuracy = (makes / attempts) * 100
        print(
            f"{distance_group}-{distance_group + 4}: {makes} made out of {attempts} attempts ({accuracy:.2f}% accuracy)")