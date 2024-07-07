# 29.06.24

import re
import sys
import json
import httpx
import logging
import urllib.parse


from bs4 import BeautifulSoup


# Logic class
from ..Class.EpisodeType import EpisodeManager
from ..Class.SeriesType import SeasonManager


class EpisodeScraper:
    def __init__(self, url):
        """
        The constructor for the EpisodeScraper class.

        Parameters:
            - url (str): The URL of the webpage to scrape.
        """
        self.url = url
        self.soup = self._get_soup()
        self.info_site = self._extract_info()
        self.stagioni = self._organize_by_season()
        
    def _get_soup(self):
        """
        Retrieves and parses the webpage content using BeautifulSoup.

        Returns:
            - BeautifulSoup: The parsed HTML content of the webpage.
        """
        try:
            response = httpx.get(self.url)
            response.raise_for_status()

            return BeautifulSoup(response.text, 'html.parser')
        
        except Exception as e:
            print(f"Error fetching the URL: {e}")
            raise

    def _extract_info(self):
        """
        Extracts the episode information from the parsed HTML.

        Returns:
            - list: A list of dictionaries containing episode information.
        """
        rows = self.soup.find_all("p", style="text-align: center;")  
        info_site = []

        # Loop through each <p> tag and extract episode information
        for i, row in enumerate(rows, start=1):
            episodes = []

            # Find all <a> tags with the specified class and extract title and link
            for episode in row.find_all("a", class_="maxbutton-2"):

                episodes.append({
                    'title': episode.text,
                    'link': episode.get('href')
                })

            # If there are episodes, add them to the info_site list
            if len(episodes) > 0:
                if i == 2:
                    title_name = rows[i-1].get_text().split("\n")[3]

                    if "Epis" not in str(title_name): 
                        info_site.append({
                            'name': title_name,
                            'episode': episodes,
                        })

                else:
                    title_name = rows[i-2].get_text() 

                    if "Epis" not in str(title_name):
                        info_site.append({
                            'name': title_name,
                            'episode': episodes,
                        })

        # For only episode
        if len(info_site) == 0:
            for i, row in enumerate(rows, start=1):

                for episode in row.find_all("a", class_="maxbutton-1"):

                    info_site.append({
                            'name': rows[i-1].get_text().split("\n")[1],
                            'url': episode.get("href"),
                        })

                    # Get obnly fist quality
                    break
                break

        return info_site

    def _organize_by_season(self):
        """
        Organizes the extracted information into seasons.

        Returns:
            - dict: A dictionary organizing episodes by season.
        """
        stagioni = {}

        # Loop through each episode dictionary and organize by season
        for dizionario in self.info_site:
            nome = dizionario["name"]

            # Use regex to search for season numbers (S01, S02, etc.)
            match = re.search(r'S\d+', nome)
            if match:
                stagione = match.group(0)
                if stagione not in stagioni:
                    stagioni[stagione] = []
                    
                stagioni[stagione].append(dizionario)

        self.is_serie = len(list(stagioni.keys())) > 0
        return stagioni

    def get_available_seasons(self):
        """
        Returns a list of available seasons.

        Returns:
            - list: A list of available seasons.
        """
        return list(self.stagioni.keys())

    def get_episodes_by_season(self, season):
        """
        Returns a list of episodes for a given season.

        Parameters:
            - season (str): The season identifier (e.g., 'S01').

        Returns:
            - list: A list of episodes for the specified season.
        """
        episodes = self.stagioni[season][0]['episode']

        def find_group_size(episodes):
            seen_titles = {}

            for index, episode in enumerate(episodes):
                title = episode["title"]

                if title in seen_titles:
                    return index - seen_titles[title]
                
                seen_titles[title] = index

            return len(episodes)  

        # Find group size
        group_size = find_group_size(episodes)

        grouped_episodes = []
        start_index = 0

        while start_index < len(episodes):
            group = episodes[start_index:start_index + group_size]
            grouped_episodes.append(group)
            start_index += group_size

        return grouped_episodes[0]

    def get_film(self):
        """
        Retrieves the first element from the info_site list.
        """
        return self.info_site[0]


class ApiManager:
    def __init__(self, url):
        """
        The constructor for the EpisodeScraper class.

        Parameters:
            - url (str): The URL of the webpage to scrape.
        """
        self.url = url
        self.episode_scraper = EpisodeScraper(url)
        self.is_serie = self.episode_scraper.is_serie

        self.obj_season_manager: SeasonManager = SeasonManager()
        self.obj_episode_manager: EpisodeManager = EpisodeManager()

    def collect_season(self):
        """
        Collect available seasons from the webpage and add them to the season manager.
        """

        available_seasons = self.episode_scraper.get_available_seasons()

        for dict_season in available_seasons:
            self.obj_season_manager.add_season({'name': dict_season})

    def collect_episode(self, season_name):  
        """
        Collect episodes for a given season and add them to the episode manager.

        Parameters:
            - season_name (str): The name of the season for which to collect episodes.
        """

        dict_episodes = self.episode_scraper.get_episodes_by_season(season_name)

        for dict_episode in dict_episodes:
            self.obj_episode_manager.add_episode(dict_episode)

    def get_film_playlist(self):
        """
        Get the film playlist from the episode scraper.

        Returns:
            - list: A list of films in the playlist.
        """
        return self.episode_scraper.get_film()
