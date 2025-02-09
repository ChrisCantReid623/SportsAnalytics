"""
analyze_rookie_contracts.py

This script analyzes rookie contract data from the file rooks_all_time.csv, identifying top contracts
and visualizing distributions for contract-related metrics.

Author: [Your Name]
Date: [Current Date]
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Use a non-interactive backend to ensure plots are saved as images
matplotlib.use('Agg')

def clean_currency_columns(data, columns):
    """Convert currency columns from strings to numeric values, ignoring non-numeric entries."""
    for column in columns:
        if column in data.columns:
            data[column] = data[column].replace(r'[\$,]', '', regex=True)
            # Convert to numeric, forcing errors to NaN
            data[column] = pd.to_numeric(data[column], errors='coerce')
    return data

def load_data(file_path):
    """Load rookie contract data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded successfully. {len(data)} rows and {len(data.columns)} columns.")
        print(f"Columns in dataset: {data.columns}")  # Debug print
        return data
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None

def top_values(data, column, top_n=10):
    """Display the top N rows for a specific column."""
    if column not in data.columns:
        print(f"Column '{column}' not found in data.")
        return None
    top_data = data.sort_values(by=column, ascending=False).head(top_n)
    return top_data

def plot_metric_distribution(data, metric, output_dir, top_n=10):
    """Plot the distribution of a specific metric, display top values, and save the plot."""
    if metric not in data.columns:
        print(f"Metric '{metric}' not found in data.")
        return

    # Display top N rows for the metric
    top_data = top_values(data, metric, top_n)
    print(f"\nTop {top_n} values for {metric}:")
    if top_data is not None:
        print(top_data[[metric]])

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Plot the metric distribution
    try:
        plt.figure(figsize=(8, 6))
        data[metric].dropna().plot(kind='hist', bins=20, title=f"Distribution of {metric}")
        plt.xlabel(metric)
        plt.ylabel("Frequency")
        plt.title(f"Distribution of {metric}")
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(f"{output_dir}/{metric}_distribution.png")  # Save the plot
        print(f"Distribution plot for {metric} saved to {output_dir}/{metric}_distribution.png")
        plt.close()
    except Exception as e:
        print(f"Error while plotting metric distribution for {metric}: {e}")

def plot_positional_distribution(data, position_column, output_dir):
    """Plot the distribution of positions as both a bar chart and pie chart, print stats, and save the plots."""
    if position_column not in data.columns:
        print(f"Position column '{position_column}' not found in data.")
        return

    # Print positional statistics
    position_counts = data[position_column].value_counts()
    print("\nPositional Distribution:")
    print(position_counts)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Plot the positional distribution as a bar chart
    try:
        plt.figure(figsize=(8, 6))
        position_counts.plot(kind='bar', color='lightblue', edgecolor='black', title="Positional Distribution (Bar Chart)")
        plt.xlabel("Position")
        plt.ylabel("Count")
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(f"{output_dir}/positional_distribution_bar.png")  # Save the bar chart
        print(f"Positional distribution bar chart saved to {output_dir}/positional_distribution_bar.png")
        plt.close()
    except Exception as e:
        print(f"Error while plotting positional distribution as a bar chart: {e}")

    # Plot the positional distribution as a pie chart
    try:
        plt.figure(figsize=(8, 8))
        position_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colormap="tab20", title="Positional Distribution (Pie Chart)")
        plt.ylabel('')  # Hide the y-label for better aesthetics
        plt.title("Positional Distribution (Pie Chart)", fontsize=16)
        plt.savefig(f"{output_dir}/positional_distribution_pie.png")  # Save the pie chart
        print(f"Positional distribution pie chart saved to {output_dir}/positional_distribution_pie.png")
        plt.close()
    except Exception as e:
        print(f"Error while plotting positional distribution as a pie chart: {e}")

def analyze_all_features(data, numeric_columns, output_dir, top_n=10):
    """Analyze all numeric features in the dataset."""
    for metric in numeric_columns:
        plot_metric_distribution(data, metric, output_dir, top_n)

if __name__ == "__main__":
    input_file = "rooks_all_time.csv"

    # Set output directory explicitly
    output_directory = "/Users/christopherreid/My Drive (christopherreid@arizona.edu)/Classes/10. Fall 2024/496 Sports Analytics/496_Project/Code/Phase_1: Rookie Contracts/contract_plots"

    # Load the rookie contracts dataset
    data = load_data(input_file)
    if data is not None:
        # Clean currency columns
        currency_columns = ["Value", "AAV", "Practical GTD"]
        data = clean_currency_columns(data, currency_columns)

        # Identify numeric columns
        numeric_columns = data.select_dtypes(include=["float64", "int64"]).columns
        print(f"Numeric columns identified: {list(numeric_columns)}")

        # Analyze all numeric features
        analyze_all_features(data, numeric_columns, output_dir=output_directory, top_n=10)

        # Plot positional distribution
        plot_positional_distribution(data, position_column="Pos", output_dir=output_directory)