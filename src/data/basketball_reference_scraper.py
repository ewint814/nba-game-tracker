"""
Basketball Reference Scraper Module

This module provides functionality to scrape game data from basketball-reference.com.
It handles fetching game schedules, box scores, and parsing game statistics.

Example:
    scraper = BasketballReferenceScraper()
    games = scraper.get_games_for_date("2024-11-25")
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

class BasketballReferenceScraper:
    """
    A class to handle all Basketball Reference scraping operations.
    
    This class provides methods to fetch and parse game data from basketball-reference.com,
    including game schedules, box scores, and detailed statistics.
    
    Attributes:
        base_url (str): The base URL for Basketball Reference website
    """

    def __init__(self):
        """Initialize the scraper with base URL."""
        self.base_url = "https://www.basketball-reference.com"
    
    def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from a URL with error handling.
        
        Args:
            url (str): The URL to fetch data from
            
        Returns:
            str: The HTML content of the page
            
        Raises:
            Exception: If the URL fetch fails or returns non-200 status
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch data from {url}. Error: {str(e)}")

    def get_games_for_date(self, date: str) -> str:
        """
        Fetch all games for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            str: HTML content containing games for the specified date
            
        Example:
            html = scraper.get_games_for_date("2024-11-25")
        """
        formatted_date = datetime.strptime(date, "%Y-%m-%d")
        url = f"{self.base_url}/boxscores/?month={formatted_date.month}&day={formatted_date.day}&year={formatted_date.year}"
        return self.fetch_html(url)

    def parse_games(self, html: str, team_filter: str = None) -> list:
        """
        Parse games from HTML content with optional team filter.
        
        Args:
            html (str): HTML content to parse
            team_filter (str, optional): Filter games for specific team
            
        Returns:
            list: List of dictionaries containing game information
            
        Example:
            games = scraper.parse_games(html, team_filter="Boston")
        """
        soup = BeautifulSoup(html, 'html.parser')
        game_summaries = soup.find_all('div', class_='game_summary expanded nohover')
        
        games = []
        for game in game_summaries:
            game_data = self._parse_game_summary(game)
            if team_filter is None or team_filter in [game_data["Winner"], game_data["Loser"]]:
                games.append(game_data)
        
        return games

    def _parse_game_summary(self, game_div: BeautifulSoup) -> dict:
        """
        Parse individual game summary div.
        
        Args:
            game_div (BeautifulSoup): BeautifulSoup object containing game summary HTML
            
        Returns:
            dict: Dictionary containing parsed game information
                Keys:
                - Winner (str): Name of winning team
                - Winner Score (int): Score of winning team
                - Loser (str): Name of losing team
                - Loser Score (int): Score of losing team
                - Box Score URL (str): URL to detailed box score
        """
        teams_table = game_div.find('table', class_='teams')
        winner_row = teams_table.find('tr', class_='winner')
        loser_row = teams_table.find('tr', class_='loser')
        
        box_score_link = game_div.find('p', class_='links').find('a', href=True)['href']
        
        return {
            "Winner": winner_row.find('td').text,
            "Winner Score": int(winner_row.find('td', class_='right').text),
            "Loser": loser_row.find('td').text,
            "Loser Score": int(loser_row.find('td', class_='right').text),
            "Box Score URL": f"{self.base_url}{box_score_link}"
        }

    def get_box_score(self, url: str) -> str:
        """
        Fetch and parse box score data from a specific game URL.
        
        Args:
            url (str): URL of the box score page
            
        Returns:
            str: HTML content of the box score page
            
        Note:
            This method currently returns raw HTML. Future updates will
            include parsed box score data.
        """
        html = self.fetch_html(url)
        # TODO: Add box score parsing logic
        return html


if __name__ == "__main__":
    # Example usage of the scraper
    scraper = BasketballReferenceScraper()
    
    # Example: Get Celtics games for yesterday
    date = "2025-02-12"
    html = scraper.get_games_for_date(date)
    games = scraper.parse_games(html, team_filter="Boston")
    
    print(f"Found {len(games)} games for {date}")
    for game in games:
        print(f"{game['Winner']} ({game['Winner Score']}) vs {game['Loser']} ({game['Loser Score']})") 