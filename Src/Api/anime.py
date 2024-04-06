# 11.03.24

import os
import logging


# External libraries
import requests


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.config import config_manager
from Src.Lib.FFmpeg.my_m3u8 import Downloader
from Src.Util.message import start_message
from .Class import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
ANIME_FOLDER = config_manager.get('DEFAULT', 'anime_folder_name')
MOVIE_FOLDER = config_manager.get('DEFAULT', 'movies_folder_name')
SERIES_FOLDER = config_manager.get('DEFAULT', 'series_folder_name')
URL_SITE_NAME = config_manager.get('SITE', 'anime_site_name')  
SITE_DOMAIN = config_manager.get('SITE', 'anime_domain')  


# Variable
video_source = VideoSource()


class EpisodeDownloader:
    def __init__(self, tv_id: int, tv_name: str, is_series: bool = True):
        """
        Initialize EpisodeDownloader class.

        Args:
            tv_id (int): The ID of the TV show.
            tv_name (str): The name of series or for film the name of film
        """
        self.tv_id = tv_id
        self.tv_name = tv_name
        self.is_series = is_series

    @staticmethod
    def manage_selection(cmd_insert: str, max_count: int):

        list_season_select = []

        # For a single number (e.g., '5')
        if cmd_insert.isnumeric():
            list_season_select.append(int(cmd_insert))

        # For a range (e.g., '[5-12]')
        elif "[" in cmd_insert:
            start, end = map(int, cmd_insert[1:-1].split("-"))
            list_season_select = list(range(start, end + 1))

        # For all seasons
        elif cmd_insert == "*":
            list_season_select = list(range(1, max_count + 1))

        # Return list of selected seasons
        return list_season_select

    def get_count_episodes(self):

        try:

            # Send a GET request to fetch information about the TV show
            response = requests.get(
                f"https://www.{URL_SITE_NAME}.{SITE_DOMAIN}/info_api/{self.tv_id}/"
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Extract the count of episodes from the JSON response
            return response.json()["episodes_count"]

        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching episode count: {e}")
            return 0

    def get_info_episode(self, index_ep: int):

        try:

            # Send a GET request to fetch information about the specific episode
            params = {"start_range": index_ep, "end_range": index_ep + 1}

            response = requests.get(
                f"https://www.{URL_SITE_NAME}.{SITE_DOMAIN}/info_api/{self.tv_id}/{index_ep}",
                params=params,
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Extract episode information from the JSON response
            return response.json()["episodes"][-1]

        except Exception as e:
            logging.error(
                f"(EpisodeDownloader) Error fetching episode information: {e}"
            )
            return None

    def get_embed(self, episode_id: int):

        try:
            # Send a GET request to fetch the embed URL for the episode
            response = requests.get(
                f"https://www.{URL_SITE_NAME}.{SITE_DOMAIN}/embed-url/{episode_id}"
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Extract the embed URL from the response
            embed_url = response.text.strip()

            # Validate the embed URL
            if not embed_url.startswith("http"):
                raise ValueError("Invalid embed URL")

            # Fetch the actual video URL using the embed URL
            video_response = requests.get(embed_url)

            # Raise an exception for bad status codes
            video_response.raise_for_status()

            # Return the video URL
            return video_response.text

        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching embed URL: {e}")
            return None

    def download_episode(self, index_select):

        # Get information about the selected episode
        info_ep_select = self.get_info_episode(index_select)

        if not info_ep_select:
            logging.error("(EpisodeDownloader) Error getting episode information.")
            return

        # Extract the ID of the selected episode
        episode_id = info_ep_select.get("id")

        start_message()
        console.print(f"[yellow]Download:  [red]{episode_id} \n")

        # Get the embed URL for the episode
        embed_url = self.get_embed(episode_id)

        if not embed_url:
            logging.error("Error getting embed URL.")
            return

        # Parse parameter in embed text
        video_source.parse_script(embed_url)

        # Download the film using the m3u8 playlist, key, and output filename
        try:

            if self.is_series:

                obj_download = Downloader(
                    m3u8_playlist=video_source.get_playlist(),
                    key=video_source.get_key(),
                    output_filename=os.path.join(
                        ROOT_PATH,
                        ANIME_FOLDER,
                        SERIES_FOLDER,
                        self.tv_name,
                        f"{index_select}.mp4",
                    ),
                )

            else:

                obj_download = Downloader(
                    m3u8_playlist=video_source.get_playlist(),
                    key=video_source.get_key(),
                    output_filename=os.path.join(
                        ROOT_PATH, 
                        ANIME_FOLDER, 
                        MOVIE_FOLDER, 
                        f"{self.tv_name}.mp4"
                    ),
                )

            obj_download.download_m3u8()

        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error downloading film: {e}")



# ONLY SERIES
def anime_download_series(tv_id: int, tv_name: str):
    """
    Function to download episodes of a TV series.

    Args:
    - tv_id (int): The ID of the TV series.
    - tv_name (str): The name of the TV series.
    """

    # Get the count of episodes for the TV series
    episodes_downloader = EpisodeDownloader(tv_id, tv_name)
    episoded_count = episodes_downloader.get_count_episodes()

    console.log(f"[cyan]Episodes find: [red]{episoded_count}")

    # Prompt user to select an episode index
    last_command = msg.ask("\n[cyan]Insert media [red]index [yellow]or [red](*) [cyan]to download all media [yellow]or [red][1-2] [cyan]for a range of media")

    # Manage user selection
    list_episode_select = EpisodeDownloader.manage_selection(last_command, episoded_count)

    # Download selected episodes
    if len(list_episode_select) == 1 and last_command != "*":
        episodes_downloader.download_episode(list_episode_select[0])

    # Download all other episodes selecter
    else:
        for i_episode in list_episode_select:
            episodes_downloader.download_episode(i_episode)


# ONLY FILM
def anime_download_film(id_film: int, title_name: str):
    """
    Function to download a film.

    Args:
    - id_film (int): The ID of the film.
    - title_name (str): The title of the film.
    """

    # Placeholder function for downloading a film
    episodes_downloader = EpisodeDownloader(id_film, title_name, is_series=False)

    # Extract the ID of the selected episode and download
    episodes_downloader.download_episode(0)

