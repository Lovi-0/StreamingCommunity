# 01.03.24

import sys
import logging
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


# External libraries
from Src.Lib.Request import requests
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.console import console, Panel


# Logic class
from ..Class.SeriesType import TitleManager
from ..Class.EpisodeType import EpisodeManager
from ..Class.PreviewType import PreviewManager
from ..Class.WindowType import WindowVideo, WindowParameter, DynamicJSONConverter


class VideoSource:
    def __init__(self):
        """
        Initialize a VideoSource object.
        """
        self.headers = {
            'user-agent': get_headers()
        }
        self.is_series = False
        self.base_name = "streamingcommunity"

    def setup(self, version: str = None, domain: str = None, media_id: int = None, series_name: str = None):
        """
        Set up the class

        Args:
            - version (str): The version to set.
            - media_id (str): The media ID to set.
            - media_id (int): The media ID to set.
            - series_name (str): The series name to set.
        """
        self.version = version
        self.domain = domain
        self.media_id = media_id

        if series_name is not None:
            self.is_series = True
            self.series_name = series_name
            self.obj_title_manager: TitleManager = TitleManager()
            self.obj_episode_manager: EpisodeManager = EpisodeManager()

    def get_preview(self) -> None:
        """
        Retrieves preview information of a media-id
        """

        try:
            
            response = requests.post(f"https://{self.base_name}.{self.domain}/api/titles/preview/{self.media_id}", headers=self.headers)
            response.raise_for_status()

            # Collect all info about preview
            self.obj_preview = PreviewManager(response.json())

        except Exception as e:
            logging.error(f"Error collecting preview info: {e}")
            raise

    def collect_info_seasons(self) -> None:
        """
        Collect information about seasons.
        """

        self.headers = {
            'user-agent': get_headers(),
            'x-inertia': 'true', 
            'x-inertia-version': self.version,
        }

        try:

            response = requests.get(f"https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}", headers=self.headers)
            response.raise_for_status()

            # Extract JSON response if available
            json_response = response.json().get('props', {}).get('title', {}).get('seasons', [])
                
            # Iterate over JSON data and add titles to the manager
            for dict_season in json_response:
                self.obj_title_manager.add_title(dict_season)

        except Exception as e:
            logging.error(f"Error collecting season info: {e}")
            raise

    def collect_title_season(self, number_season: int) -> None:
        """
        Collect information about a specific season.

        Args:
            - number_season (int): The season number.
        """
        try:

            # Make a request to collect information about a specific season
            response = requests.get(f'https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}/stagione-{number_season}', headers=self.headers)
            response.raise_for_status()

            # Extract JSON response if available
            json_response = response.json().get('props', {}).get('loadedSeason', {}).get('episodes', [])
                
            # Iterate over JSON data and add episodes to the manager
            for dict_episode in json_response:
                self.obj_episode_manager.add_episode(dict_episode)

        except Exception as e:
            logging.error(f"Error collecting title season info: {e}")
            raise

    def get_iframe(self, episode_id: int = None) -> None:
        """
        Get iframe source.

        Args:
            - episode_id (int): The episode ID, present only for series
        """
        params = {}

        if self.is_series:
            params = {
                'episode_id': episode_id, 
                'next_episode': '1'
            }

        try:

            # Make a request to get iframe source
            response = requests.get(f"https://{self.base_name}.{self.domain}/iframe/{self.media_id}", params=params)
            response.raise_for_status()

            # Parse response with BeautifulSoup to get iframe source
            soup = BeautifulSoup(response.text, "html.parser")
            self.iframe_src = soup.find("iframe").get("src")

        except Exception as e:
            logging.error(f"Error getting iframe source: {e}")
            raise

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

    def get_content(self) -> None:
        """
        Get content.
        """
        try:

            # Check if iframe source is available
            if self.iframe_src is not None:

                # Make a request to get content
                try:
                    response = requests.get(self.iframe_src, headers=self.headers)
                    response.raise_for_status()

                except:
                    print("\n")
                    console.print(Panel("[red bold]Coming soon", title="Notification", title_align="left", border_style="yellow"))
                    sys.exit(0)

                if response.ok:

                    # Parse response with BeautifulSoup to get content
                    soup = BeautifulSoup(response.text, "html.parser")
                    script = soup.find("body").find("script").text

                    # Parse script to get video information
                    self.parse_script(script_text=script)

        except Exception as e:
            logging.error(f"Error getting content: {e}")
            raise


    def get_playlist(self) -> str:
        """
        Get playlist.

        Returns:
            str: The playlist URL, or None if there's an error.
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