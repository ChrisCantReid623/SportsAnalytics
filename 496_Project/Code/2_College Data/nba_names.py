import pandas as pd


# Function to extract first and last names and save to a new CSV
def extract_player_names(input_csv, output_csv):
    """
    Extracts the first and last names of players from the input CSV file,
    sorts them alphabetically by last name, and saves them into a new CSV file.

    Args:
    input_csv (str): The path to the input CSV file containing player data.
    output_csv (str): The path to the output CSV file to save first and last names.
    """
    # Read the input CSV file
    df = pd.read_csv(input_csv)

    # Ensure 'Player' column exists
    if 'Player' not in df.columns:
        print(f"Error: 'Player' column not found in {input_csv}")
        return

    # Split the 'Player' column into first and last names
    names_split = df['Player'].str.split(' ', n=1, expand=True)

    # Rename the split columns
    names_split.columns = ['First Name', 'Last Name']

    # Sort the DataFrame by 'Last Name'
    df_sorted = names_split.sort_values(by='Last Name')

    # Save the sorted DataFrame to the output CSV file
    df_sorted.to_csv(output_csv, index=False)

    print(f"First and last names have been extracted, sorted, and saved to {output_csv}")


# Main function
def main():
    # Input CSV file path
    input_csv = "/Users/christopherreid/My Drive (christopherreid@arizona.edu)/Classes/10. Fall 2024/496 Sports Analytics/496_Project/Code/Phase_1: Rookie Contracts/rooks_all_time.csv"

    # Output CSV file path
    output_csv = "player_names_sorted.csv"  # Replace with your desired output CSV path

    # Extract player names, sort by last name, and save to a new CSV
    extract_player_names(input_csv, output_csv)


if __name__ == "__main__":
    main()