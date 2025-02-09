"""
contract_categorizer.py
Author: Christopher Reid
Date: October 2024

Description:
This script reads NBA rookie contract extension data from a CSV file and allows the user to categorize and sort the data
by a chosen column. Special handling is done for monetary columns ('Value', 'AAV', 'Practical GTD'), which are displayed
in an alternate table format sorted in ascending order. Additionally, the selected column will be highlighted in yellow.

Instructions:
- This script requires the 'pandas' library.
- You can install it using:
    pip install pandas
"""

import os
import pandas as pd

# Set pandas display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.max_colwidth', None)

def display_key():
    """
    Display a numbered key for the headers for easier access, with notes about special money formats.
    """
    headers = {
        1: 'YR_1',
        2: 'Pos',
        3: 'Age At Signing',
        4: 'Yrs',
        5: 'Value (..alt table format)',
        6: 'AAV (..alt table format)',
        7: 'Practical GTD (..alt table format)',
        8: 'Type'
    }

    print("Column Key:")
    for number, column in headers.items():
        print(f"{number}: {column}")

    return headers

def clean_money_columns(df, column_name):
    """
    Clean columns that represent monetary values (e.g., 'Value', 'AAV', 'Practical GTD') by
    removing dollar signs and commas, and converting the column to numeric values.
    """
    df[column_name] = pd.to_numeric(df[column_name].replace(r'[\$,]', '', regex=True), errors='coerce')

def print_sorted_table_with_highlight(df, highlight_column):
    # Define the column order with 'Player' as the first column
    column_order = ['Player', 'YR_1', 'Rank', 'Pos', 'Team Signed With', 'Age At Signing', 'Yrs', 'Value', 'AAV', 'Practical GTD', 'Type']

    # Define the column widths
    column_widths = {
        'Player': 25,  # Enough space for the longest name
        'YR_1': 6,
        'Rank': 6,
        'Pos': 5,
        'Team Signed With': 15,
        'Age At Signing': 18,
        'Yrs': 6,
        'Value': 15,
        'AAV': 15,
        'Practical GTD': 18,
        'Type': 30
    }

    # Print the headers
    headers = []
    for col in column_order:
        headers.append(f"{col:<{column_widths[col]}}")
    print('   '.join(headers))

    # Print a separator
    print('-' * (sum(column_widths.values()) + (len(column_widths) - 1) * 3))

    # Print the rows
    for index, row in df.iterrows():
        row_data = []
        for col in column_order:
            # Highlight the chosen column in yellow
            if col == highlight_column:
                row_data.append(f"\033[93m{str(row[col]):<{column_widths[col]}}\033[0m")
            else:
                row_data.append(f"{str(row[col]):<{column_widths[col]}}")
        print('   '.join(row_data))

def sort_and_categorize_players_by_column(df, column_number):
    """
    Sorts and categorizes players based on the chosen column (selected by the user).
    Handles monetary and non-monetary columns appropriately.

    Args:
    - df (pandas.DataFrame): The dataframe containing player data.
    - column_number (int): The number corresponding to the selected column.
    """
    # Map column numbers to column names in the DataFrame
    headers = {
        1: 'YR_1',
        2: 'Pos',
        3: 'Age At Signing',
        4: 'Yrs',
        5: 'Value',
        6: 'AAV',
        7: 'Practical GTD',
        8: 'Type'
    }

    # Get the column name based on user input
    column_name = headers.get(column_number, None)

    if not column_name:
        print("Invalid column number. Please try again.")
        return

    # Check if the selected column is a monetary one
    if column_name in ['Value', 'AAV', 'Practical GTD']:
        # Clean the monetary columns to remove currency symbols and convert to numeric values
        clean_money_columns(df, column_name)

    # Sort the dataframe by the selected column
    df = df.sort_values(by=[column_name])

    # Print the table sorted by the chosen column with 'Player' as the first column
    print_sorted_table_with_highlight(df, column_name)

    # If sorting by 'Pos', calculate and display position counts with aligned output
    if column_name == 'Pos':
        print("\nPosition Counts:")
        position_counts = df['Pos'].value_counts()

        # Find the longest position string for alignment purposes
        max_pos_length = max(len(pos) for pos in position_counts.index)

        # Print aligned position counts
        for pos, count in position_counts.items():
            print(f"{pos:<{max_pos_length}} : {count}")

    # If sorting by 'Age At Signing', calculate and display age counts with aligned output
    elif column_name == 'Age At Signing':
        print("\nAge At Signing Counts:")
        age_counts = df['Age At Signing'].value_counts().sort_index()

        # Find the longest age string for alignment purposes (in case of non-integer values)
        max_age_length = max(len(str(age)) for age in age_counts.index)

        # Print aligned age counts
        for age, count in age_counts.items():
            print(f"{age:<{max_age_length}} : {count}")

    # If sorting by 'Yrs', calculate and display years counts with aligned output
    elif column_name == 'Yrs':
        print("\nYears (Yrs) Counts:")
        yrs_counts = df['Yrs'].value_counts().sort_index()

        # Find the longest year string for alignment purposes (in case of non-integer values)
        max_yrs_length = max(len(str(yrs)) for yrs in yrs_counts.index)

        # Print aligned years counts
        for yrs, count in yrs_counts.items():
            print(f"{yrs:<{max_yrs_length}} : {count}")

def list_csv_files():
    """
    Lists all CSV files in the same directory as the script.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Directory of the current script
    csv_files = [f for f in os.listdir(script_dir) if f.endswith('.csv')]  # Search for CSV files in the same directory
    if not csv_files:
        print("No CSV files found in the current directory.")
        return None

    print("CSV files found in the same directory as the script:")
    for index, csv_file in enumerate(csv_files, start=1):
        print(f"{index}: {csv_file}")

    return csv_files

def main():
    """
    Main function to read the CSV file and ask the user for a header to categorize and sort by.
    """
    # Scan the script's directory for CSV files
    csv_files = list_csv_files()

    if not csv_files:
        return

    # Ask the user to choose a CSV file
    try:
        file_choice = int(input("Enter the number corresponding to the CSV file you want to use: "))
        if 1 <= file_choice <= len(csv_files):
            selected_file = csv_files[file_choice - 1]
        else:
            print("Invalid file choice. Exiting.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    print()  # Add a blank line before moving to column selection

    # Read the selected CSV file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    selected_file_path = os.path.join(script_dir, selected_file)
    df = pd.read_csv(selected_file_path)

    # Enter a loop to keep prompting the user for sorting options
    while True:
        print()  # Add a blank line for better readability

        # Display the column key with a blank line before it
        headers = display_key()

        print()  # Add a blank line after displaying the column key

        # Ask the user to choose a column for sorting or exit
        user_input = input("Enter the number corresponding to the column you want to categorize and sort by (or type 'exit' to quit): ").strip()

        if user_input.lower() == 'exit':
            print("Exiting the program. Goodbye!")
            break

        try:
            column_number = int(user_input)
            if column_number in headers:
                sort_and_categorize_players_by_column(df, column_number)
            else:
                print("Invalid column number.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()