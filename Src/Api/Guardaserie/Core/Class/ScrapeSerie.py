# 13.06.24

import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers


# Logic class
from .SearchType import MediaItem



class GetSerieInfo:

    def __init__(self, dict_serie: MediaItem = None) -> None:
        """
        Initializes the VideoSource object with default values.

        Attributes:
            headers (dict): An empty dictionary to store HTTP headers.
        """
        self.headers = {'user-agent': get_headers()}
        self.url = dict_serie.url
        self.tv_name = None
        self.list_episodes = None

    def get_seasons_number(self):

        response = httpx.get(self.url, headers=self.headers)

        # Create soup and find table
        soup = BeautifulSoup(response.text, "html.parser")
        table_content = soup.find('div', class_="tt_season")

        seasons_number = len(table_content.find_all("li"))
        self.tv_name = soup.find("h1", class_= "front_title").get_text(strip=True)
        
        return seasons_number
    
    def get_episode_number(self, n_season: int):

        response = httpx.get(self.url, headers=self.headers)

        # Create soup and find table
        soup = BeautifulSoup(response.text, "html.parser")
        table_content = soup.find('div', class_="tab-pane", id=f"season-{n_season}")

        # Scrape info episode
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