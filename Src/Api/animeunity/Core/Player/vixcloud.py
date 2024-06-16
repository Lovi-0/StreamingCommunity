# 01.03.24

import sys
import logging
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util._jsonConfig import config_manager


# Logic class
from ..Class.SeriesType import TitleManager
from ..Class.EpisodeType import EpisodeManager, Episode
from ..Class.WindowType import WindowVideo, WindowParameter, DynamicJSONConverter


# Variable
from ...costant import SITE_NAME


class VideoSource:
    def __init__(self):
        """
        Initialize a VideoSource object.
        """
        self.headers = {
            'user-agent': get_headers()
        }
        self.is_series = False
        self.base_name = SITE_NAME
        self.domain = config_manager.get('SITE', self.base_name)  

    def setup(self, media_id: int = None, series_name: str = None):
        """
        Set up the class

        Args:
            - media_id (int): The media ID to set.
            - series_name (str): The series name to set.
        """
        self.media_id = media_id

        if series_name is not None:
            self.is_series = True
            self.series_name = series_name
            self.obj_title_manager: TitleManager = TitleManager()
            self.obj_episode_manager: EpisodeManager = EpisodeManager()
            
    def get_count_episodes(self):
        """
        Fetches the total count of episodes available for the anime.
        
        Returns:
            int or None: Total count of episodes if successful, otherwise None.
        """
        try:

            response = httpx.get(f"https://www.{self.base_name}.{self.domain}/info_api/{self.media_id}/")
            response.raise_for_status()

            # Parse JSON response and return episode count
            return response.json()["episodes_count"]
        
        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching episode count: {e}")
            return None
    
    def get_info_episode(self, index_ep: int) -> Episode:
        """
        Fetches information about a specific episode.
        
        Args:
            - index_ep (int): Index of the episode.
            
        Returns:
            obj Episode or None: Information about the episode if successful, otherwise None.
        """
        try:

            params = {
                "start_range": index_ep, 
                "end_range": index_ep + 1
            }

            response = httpx.get(f"https://www.{self.base_name}.{self.domain}/info_api/{self.media_id}/{index_ep}", params = params)
            response.raise_for_status()

            # Return information about the episode
            json_data = response.json()["episodes"][-1]
            return Episode(json_data)
        
        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching episode information: {e}")
            return None
    
    def get_embed(self, episode_id: int):
        """
        Fetches the script text for a given episode ID.
        
        Args:
            - episode_id (int): ID of the episode.
            
        Returns:
            str or None: Script successful, otherwise None.
        """
        try:

            response = httpx.get(f"https://www.{self.base_name}.{self.domain}/embed-url/{episode_id}")
            response.raise_for_status()

            # Extract and clean embed URL
            embed_url = response.text.strip()
            self.iframe_src = embed_url

            # Fetch video content using embed URL
            video_response = httpx.get(embed_url)
            video_response.raise_for_status()


            # Parse response with BeautifulSoup to get content of the scriot
            soup = BeautifulSoup(video_response.text, "html.parser")
            script = soup.find("body").find("script").text

            return script
        
        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching embed URL: {e}")
            return None

    def parse_script(self, script_text: str) -> None:
        """
        Parse script text.

        Args:
            - script_text (str): The script text to parse.
        """
        try:

            converter = DynamicJSONConverter(script_text)
            result = converter.convert_to_dynamic_json()

            # Create window video and parameter objects
            self.window_video = WindowVideo(result['video'])
            self.window_parameter = WindowParameter(result['masterPlaylist'])

        except Exception as e:
            logging.error(f"Error parsing script: {e}")
            raise

    def get_playlist(self) -> str:
        """
        Get playlist.

        Returns:
            - str: The playlist URL, or None if there's an error.
        """

        iframe_url = self.iframe_src

        # Create base uri for playlist
        base_url = f'https://vixcloud.co/playlist/{self.window_video.id}'
        query = urlencode(list(self.window_parameter.data.items()))
        master_playlist_url = urljoin(base_url, '?' + query)

        # Parse the current query string and the master playlist URL query string
        current_params = parse_qs(iframe_url[1:])  
        m = urlparse(master_playlist_url)  
        master_params = parse_qs(m.query) 

        # Create the final parameters dictionary with token and expires from the master playlist
        final_params = { 
            "token": master_params.get("token", [""])[0], 
            "expires": master_params.get("expires", [""])[0] 
        }

        # Add conditional parameters
        if "b" in current_params:
            final_params["b"] = "1"   
        if "canPlayFHD" in current_params:
            final_params["h"] = "1" 

        # Construct the new query string and final URL
        new_query = urlencode(final_params)         # Encode final_params into a query string
        new_url = m._replace(query=new_query)       # Replace the old query string with the new one
        final_url = urlunparse(new_url)             # Construct the final URL from the modified parts

        return final_url
