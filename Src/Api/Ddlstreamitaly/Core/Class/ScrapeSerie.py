# 13.06.24

import sys
import logging

from typing import List, Dict


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util._jsonConfig import config_manager


# Logic class
from .SearchType import MediaItem



class GetSerieInfo:

    def __init__(self, dict_serie: MediaItem) -> None:
        """
        Initializes the GetSerieInfo object with default values.

        Args:
            dict_serie (MediaItem): Dictionary containing series information (optional).
        """
        self.headers = {'user-agent': get_headers()}
        self.cookies = config_manager.get_dict('REQUESTS', 'index')
        self.url = dict_serie.url
        self.tv_name = None
        self.list_episodes = None

    def get_episode_number(self) -> List[Dict[str, str]]:
        """
        Retrieves the number of episodes for a specific season.

        Args:
            n_season (int): The season number.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing episode information.
        """

        # Make an HTTP request to the series URL
        try:
            response = httpx.get(self.url + "?area=online", cookies=self.cookies, headers=self.headers)
            response.raise_for_status()

        except Exception as e:
            logging.error(f"Insert: ['ips4_device_key': 'your_code', 'ips4_member_id': 'your_code', 'ips4_login_key': 'your_code'] in config file \ REQUESTS \ index, instead of user-agent. Use browser debug and cookie request with a valid account, filter by DOC.")
            sys.exit(0)

        # Parse HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Get tv name 
        self.tv_name = soup.find("span", class_= "ipsType_break").get_text(strip=True)

        # Find the container of episodes for the specified season
        table_content = soup.find('div', class_='ipsMargin_bottom:half')
        list_dict_episode = []

        for episode_div in table_content.find_all('a', href=True):

            # Get text of episode
            part_name = episode_div.get_text(strip=True)

            if part_name:
                link = episode_div['href']

                obj_episode = {
                    'name': part_name,
                    'url': link
                }
                list_dict_episode.append(obj_episode)
     
        self.list_episodes = list_dict_episode
        return list_dict_episode
        