"""
alltime_rookie_contracts.py
Author: Christopher Reid
Date: October 2024

Description:
This script fetches NBA rookie contract extension data for all-time from the Spotrac website
(https://www.spotrac.com/nba/contracts/extensions/_/year/all-time/sort/type) and parses the relevant information
from the HTML. It outputs the data to the console with color formatting for contract types and creates a CSV file
('rooks_all_time.csv') with the gathered data.

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


def fetch_all_time_extension_data(delay=2):
    """
    Fetches NBA rookie contract extension data for all-time from Spotrac, including headers, and appends the data to a list.
    Also, scrapes the player's draft year (YR_1) from each player's hyperlink in Spotrac.

    Args:
    - delay (int): Time to wait (in seconds) between requests to avoid being blocked.

    Returns:
    - contract_data (list): A list of lists, each containing player contract data for all-time.
    """
    url = 'https://www.spotrac.com/nba/contracts/extensions/_/year/all-time/sort/type'
    contract_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table')
        rows = table.find_all('tr') if table else []

        print("--- All-Time Rookie Contract Extensions ---\n")

        # Print the column headers after the separator
        headers = ['YR_1', 'Rank', 'Player', 'Pos', 'Team Signed With', 'Age At Signing', 'Yrs', 'Value', 'AAV', 'Practical GTD', 'Type']
        print(headers)
        print()  # Add a blank line before data starts printing

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
                    print_contract_with_color(data, contract_type_cell.get_text().strip().lower())

                    # Sleep between requests to avoid overloading Spotrac's server
                    time.sleep(delay)

        if not contract_data:
            print("No rookie contract extensions found for the all-time period.")

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

def create_csv(data, filename='rooks_all_time.csv'):
    """
    Writes the fetched contract data to a CSV file.

    Args:
    - data (list): The contract data to write to the CSV.
    - filename (str): The name of the CSV file.

    Returns:
    - None
    """
    headers = ['YR_1', 'Rank', 'Player', 'Pos', 'Team Signed With', 'Age At Signing', 'Yrs', 'Value', 'AAV', 'Practical GTD', 'Type']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Data has been written to {filename}")

def main():
    """
    Main function to fetch NBA rookie contract extension data for the all-time period
    and create a CSV file. It also prints the data with color formatting to the console.
    """
    # Fetch all-time rookie extension data
    all_data = fetch_all_time_extension_data()

    # Create the CSV file with the fetched data
    create_csv(all_data)

if __name__ == "__main__":
    main()