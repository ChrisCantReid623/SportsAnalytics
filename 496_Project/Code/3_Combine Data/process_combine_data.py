"""
process_combine_data.py

This script is responsible for loading, cleaning, and processing NBA Draft Combine data.
It handles missing values, standardizes numerical formats, and saves cleaned data to a new file.

Author: [Your Name]
Date: [Current Date]
"""

import pandas as pd


def load_data(file_path):
    """Load combine data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded successfully. {len(data)} rows and {len(data.columns)} columns.")
        return data
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None


def clean_data(data):
    """Clean the combine data by handling missing values and standardizing formats."""
    data.fillna("-", inplace=True)  # Replace NaN values with "-"
    data['Lane Agility'] = pd.to_numeric(data['Lane Agility'], errors='coerce')  # Convert to numeric
    data['Shuttle Run'] = pd.to_numeric(data['Shuttle Run'], errors='coerce')
    data['Three Quarter Sprint'] = pd.to_numeric(data['Three Quarter Sprint'], errors='coerce')
    data['Standing Vertical'] = pd.to_numeric(data['Standing Vertical'], errors='coerce')
    data['Max Vertical'] = pd.to_numeric(data['Max Vertical'], errors='coerce')
    data['Bench Press'] = pd.to_numeric(data['Bench Press'], errors='coerce')
    return data


def save_cleaned_data(data, output_path):
    """Save the cleaned data to a new CSV file."""
    data.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")


if __name__ == "__main__":
    input_file = "combine_agility_all_seasons.csv"
    output_file = "combine_cleaned_data.csv"

    raw_data = load_data(input_file)
    if raw_data is not None:
        cleaned_data = clean_data(raw_data)
        save_cleaned_data(cleaned_data, output_file)