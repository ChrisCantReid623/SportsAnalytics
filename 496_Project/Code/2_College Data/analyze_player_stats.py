"""
analyze_player_stats.py

This script analyzes player stats data, identifying top performers and visualizing
distributions for all numeric metrics.

Author: [Your Name]
Date: [Current Date]
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def load_data(file_path):
    """Load player stats data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded successfully. {len(data)} rows and {len(data.columns)} columns.")
        return data
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None


def top_performers(data, metric, top_n=10):
    """Get the top N performers for a specific metric."""
    if metric not in data.columns:
        print(f"Metric '{metric}' not found in data.")
        return None
    top = data.dropna(subset=[metric]).nlargest(top_n, metric)
    return top[['Player', metric]]


def plot_metric_distribution(data, metric, output_dir="plots"):
    """Plot the distribution of a specific metric and save the plot."""
    if metric not in data.columns:
        print(f"Metric '{metric}' not found in data.")
        return

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Plot the metric distribution
    data[metric].dropna().plot(kind='hist', bins=20, title=f"Distribution of {metric}")
    plt.xlabel(metric)
    plt.ylabel("Frequency")
    plt.title(f"Distribution of {metric}")
    plt.savefig(f"{output_dir}/{metric}_distribution.png")  # Save the plot
    print(f"Distribution plot for {metric} saved to {output_dir}/{metric}_distribution.png")
    plt.close()


def analyze_all_metrics(data, numeric_columns, top_n=10, output_dir="plots"):
    """Analyze all numeric metrics in the dataset."""
    for metric in numeric_columns:
        print(f"\nAnalyzing {metric}...")
        print(f"Top {top_n} performers for {metric}:")
        top_performers_list = top_performers(data, metric, top_n)
        if top_performers_list is not None:
            print(top_performers_list)
        plot_metric_distribution(data, metric, output_dir)


if __name__ == "__main__":
    input_file = "player_stats.csv"
    output_directory = "plots"  # Directory to save plots

    # Load the player stats dataset
    data = load_data(input_file)
    if data is not None:
        # Identify numeric columns
        numeric_columns = data.select_dtypes(include=["float64", "int64"]).columns
        print(f"Numeric columns identified: {list(numeric_columns)}")

        # Analyze all numeric metrics
        analyze_all_metrics(data, numeric_columns, top_n=10, output_dir=output_directory)