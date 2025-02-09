"""
combineAgility.py

This script navigates to NBA draft combine strength and agility data pages for all available seasons,
extracts all rows containing player data, and saves all seasons' data into a single CSV file.

Requirements:
    - Selenium and ChromeDriver
    - BeautifulSoup from bs4 library
    - pandas (optional, for CSV export)
    - Internet connection to access NBA's stats pages

"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

TIMEOUT = 10  # Set timeout in seconds

# Global DataFrame to hold all season data
all_data = pd.DataFrame()

# Function to navigate to the combine data page for a specific season and extract all table rows
def scrape_all_rows(season_year):
    global all_data
    url = f"https://www.nba.com/stats/draft/combine-strength-agility?SeasonYear={season_year}"

    # Set up Selenium WebDriver (adjust the path if needed)
    driver = webdriver.Chrome()  # or specify path to chromedriver if required
    driver.get(url)

    # Allow time for the page to load content fully
    time.sleep(TIMEOUT)

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find the table containing player data
    table = soup.find('table', class_='Crom_table__p1iZz')
    if not table:
        print(f"Player data table not found for season {season_year}.")
        return

    # Extract all rows in the table
    all_rows = []
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        row_data = [col.text.strip() if col.text.strip() else "-" for col in columns]
        row_data.append(season_year)  # Add season year as a new column
        all_rows.append(row_data)

    # Convert rows to DataFrame
    df = pd.DataFrame(all_rows, columns=["Player Name", "Position", "Lane Agility", "Shuttle Run", "Three Quarter Sprint", "Standing Vertical", "Max Vertical", "Bench Press", "Season Year"])

    # Append to global DataFrame
    all_data = pd.concat([all_data, df], ignore_index=True)
    print(f"Data for season {season_year} added.")

# Main function to iterate through all seasons
def scrape_all_seasons(start_year, end_year):
    for year in range(start_year, end_year + 1):
        season_year = f"{year}-{str(year + 1)[-2:]}"
        print(f"Scraping season: {season_year}")
        scrape_all_rows(season_year)
        time.sleep(1)  # Brief pause between requests to avoid overwhelming the server

    # Save the combined data to a single CSV file
    all_data.to_csv("combine_agility_all_seasons.csv", index=False)
    print("All seasons' data saved to combine_agility_all_seasons.csv.")

# Example usage: scrape from 2000-01 to 2024-25
if __name__ == '__main__':
    scrape_all_seasons(2000, 2024)