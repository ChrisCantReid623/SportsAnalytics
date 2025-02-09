"""
college_basketball_scraper.py
Author: Christopher Reid
Date: October 2024

Description:
This script scrapes player information from the Sports Reference College Basketball players page
and prints the information.

Requirements:
- requests
- BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup

# Function to scrape player information from the given URL
def scrape_player_info():
    """
    Scrapes player names and their relevant data from the Sports Reference College Basketball players page.
    """
    url = "https://www.sports-reference.com/cbb/players/"

    # Send a GET request to the website
    response = requests.get(url)

    if response.status_code == 200:
        print("Successfully connected to the site!")

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the player data
        player_table = soup.find('table', {'id': 'players'})

        if player_table:
            print("Player table found. Extracting data...\n")

            # Extract all rows from the table body
            table_body = player_table.find('tbody')
            rows = table_body.find_all('tr')

            # Loop through each row and extract player information
            for row in rows:
                # Extract player name and URL to the player's stats page
                player_cell = row.find('th', {'data-stat': 'player'})
                player_name = player_cell.text
                player_url = player_cell.find('a')['href']

                # Extract other player-related stats (e.g., year, school)
                year_cell = row.find('td', {'data-stat': 'year_min'})
                school_cell = row.find('td', {'data-stat': 'college_name'})

                player_year = year_cell.text if year_cell else 'N/A'
                player_school = school_cell.text if school_cell else 'N/A'

                # Print player information
                print(f"Player: {player_name}")
                print(f"Year: {player_year}")
                print(f"School: {player_school}")
                print(f"Profile URL: https://www.sports-reference.com{player_url}")
                print("-" * 40)
        else:
            print("Player table not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def main():
    # Scrape player information
    scrape_player_info()

if __name__ == "__main__":
    main()