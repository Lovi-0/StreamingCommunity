# 13.06.24

import logging
from typing import List, Dict


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util.headers import get_headers


# Logic class
from StreamingCommunity.Src.Api.Template .Class.SearchType import MediaItem


class GetSerieInfo:
    def __init__(self, dict_serie: MediaItem) -> None:
        """
        Initializes the GetSerieInfo object with default values.

        Parameters:
            dict_serie (MediaItem): Dictionary containing series information (optional).
        """
        self.headers = {'user-agent': get_headers()}
        self.url = dict_serie.url
        self.tv_name = None
        self.list_episodes = None

    def get_seasons_number(self) -> int:
        """
        Retrieves the number of seasons of a TV series.

        Returns:
            int: Number of seasons of the TV series.
        """
        try:

            # Make an HTTP request to the series URL
            response = httpx.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the container of seasons
            table_content = soup.find('div', class_="tt_season")

            # Count the number of seasons
            seasons_number = len(table_content.find_all("li"))

            # Extract the name of the series
            self.tv_name = soup.find("h1", class_="front_title").get_text(strip=True)

            return seasons_number

        except Exception as e:
            logging.error(f"Error parsing HTML page: {e}")

        return -999

    def get_episode_number(self, n_season: int) -> List[Dict[str, str]]:
        """
        Retrieves the number of episodes for a specific season.

        Parameters:
            n_season (int): The season number.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing episode information.
        """
        try:

            # Make an HTTP request to the series URL
            response = httpx.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the container of episodes for the specified season
            table_content = soup.find('div', class_="tab-pane", id=f"season-{n_season}")

            # Extract episode information
            episode_content = table_content.find_all("li")
            list_dict_episode = []

            for episode_div in episode_content:
                index = episode_div.find("a").get("data-num")
                link = episode_div.find("a").get("data-link")
                name = episode_div.find("a").get("data-title")

                obj_episode = {
                    'number': index,
                    'name': name,
                    'url': link
                }
                
                list_dict_episode.append(obj_episode)

            self.list_episodes = list_dict_episode
            return list_dict_episode
        
        except Exception as e:
            logging.error(f"Error parsing HTML page: {e}")

        return []
