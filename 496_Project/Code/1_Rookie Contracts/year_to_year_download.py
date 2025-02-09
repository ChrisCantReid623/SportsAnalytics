"""
year_to_year_download.py
Author: Christopher Reid
Date: October 2024

Description:
This script fetches NBA rookie contract extension data for a given range of years from the Spotrac website
(https://www.spotrac.com/nba/contracts/extensions) and parses the relevant information from the HTML.
It outputs the data to the console with color formatting for contract types and creates a CSV file
('rooks[start_year]-[end_year].csv') with the gathered data.

Instructions:
- This script requires the 'requests' and 'beautifulsoup4' libraries.
- You can install them using:
    pip install requests
    pip install beautifulsoup4
"""

import requests
import time
from bs4 import BeautifulSoup
import csv


def fetch_extension_data(year, delay=2):
    """
    Fetches NBA contract extension data for a given year from Spotrac, including headers, and appends the data to a list.
    Also, scrapes the player's draft year (YR_1) from each player's hyperlink in Spotrac.

    Args:
    - year (int): The NBA season start year for which to fetch data (e.g., 2020 for the 2020-21 season).
    - delay (int): Time to wait (in seconds) between requests to avoid being blocked.

    Returns:
    - contract_data (list): A list of lists, each containing player contract data for that year.
    """
    url = f'https://www.spotrac.com/nba/contracts/extensions/_/year/{year}/sort/value'
    contract_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table')
        rows = table.find_all('tr') if table else []

        # Print heading for the season after the separator
        print(f"--- Rookie Contract Extensions for {year}-{year + 1} Season ---")

        # Print the column headers after the separator
        headers = ['YR_1', 'Rank', 'Player', 'Pos', 'Team Signed With', 'Age At Signing', 'Yrs', 'Value', 'AAV', 'Practical GTD', 'Type']
        print(headers)

        if rows:
            for row in rows:
                contract_type_cell = row.find('td', class_='contract-type')
                if contract_type_cell and 'rookie' in contract_type_cell.get_text().lower():
                    columns = row.find_all('td')
                    data = [col.get_text(strip=True) for col in columns]

                    player_link = row.find('a', class_='link')
                    if player_link:
                        player_url = player_link['href']
                        if player_url.startswith('/'):
                            full_player_url = f'https://www.spotrac.com{player_url}'
                        else:
                            full_player_url = player_url

                        draft_year = scrape_draft_year_from_spotrac(full_player_url)
                        data.insert(0, draft_year if draft_year else "N/A")

                    contract_data.append(data)

                    # Print contract with appropriate color formatting
                    contract_type = contract_type_cell.get_text().strip().lower()
                    print_contract_with_color(data, contract_type)
        else:
            print(f"No rookie contract extensions for {year}-{year + 1} season.")

        # Ensure there's a blank line after each year
        print()
        time.sleep(delay)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")

    return contract_data

def scrape_draft_year_from_spotrac(player_url):
    """
    Scrapes the player's draft year from their Spotrac page.

    Args:
    - player_url (str): The URL of the player's Spotrac page.

    Returns:
    - draft_year (str): The draft year extracted from the player's page, or None if not found.
    """
    try:
        player_response = requests.get(player_url)
        player_response.raise_for_status()
        player_soup = BeautifulSoup(player_response.text, 'html.parser')

        divs = player_soup.find_all('div', class_='col-md-12 text-white')

        for div in divs:
            if 'Drafted:' in div.get_text():
                draft_span = div.find('span', class_='text-yellow')
                if draft_span:
                    draft_info = draft_span.get_text(strip=True)
                    draft_year = draft_info.split(',')[-1].strip()
                    return draft_year
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching player data from URL: {e}")
        return None

def print_contract_with_color(data, contract_type):
    """
    Prints contract data with color formatting based on the type of contract.

    Args:
    - data (list): A list of contract data.
    - contract_type (str): The type of contract (used for color-coding).
    """
    if 'rookie maximum extension' in contract_type.replace('-', ' '):
        print(f"\033[92m{data}\033[0m")  # Green for Rookie Maximum Extension
    elif 'designated rookie extension' in contract_type:
        print(f"\033[93m{data}\033[0m")  # Yellow for Designated Rookie Extension
    elif 'rookie extension' in contract_type:
        print(f"\033[91m{data}\033[0m")  # Red for Rookie Extension
    else:
        print(data)  # Default print for other contract types

def create_csv(data, start_year, end_year):
    """
    Writes the fetched contract data to a CSV file.

    Args:
    - data (list): The contract data to write to the CSV.
    - start_year (int): The start year of the data range.
    - end_year (int): The end year of the data range.

    Returns:
    - None
    """
    filename = f'rooks{start_year}-{end_year}.csv'
    headers = ['YR_1', 'Rank', 'Player', 'Pos', 'Team Signed With', 'Age At Signing', 'Yrs', 'Value', 'AAV', 'Practical GTD', 'Type']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Data has been written to {filename}")

def main():
    """
    Main function to fetch NBA rookie contract extension data for a user-defined range of years
    and create a CSV file. It also prints the data with color formatting to the console.
    """
    # Prompt the user for the start and end year
    try:
        start_year = int(input("Enter the start year (e.g., 2013): "))
        end_year = int(input("Enter the end year (e.g., 2023): "))

        if start_year > end_year:
            print("Start year cannot be greater than end year. Please try again.")
            return

    except ValueError:
        print("Please enter valid years.")
        return

    # Add a blank line after the user inputs
    print()

    all_data = []

    # Fetch data for the range of years
    for year in range(start_year, end_year + 1):
        year_data = fetch_extension_data(year, delay=2)
        if year_data:
            all_data.extend(year_data)

    # Create the CSV file
    create_csv(all_data, start_year, end_year)

if __name__ == "__main__":
    main()