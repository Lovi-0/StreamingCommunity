# 01.03.24

import requests
import re
import json
import binascii
import logging
from urllib.parse import urljoin, urlencode, quote


# External libraries
import requests
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers
from .SeriesType import TitleManager
from .EpisodeType import EpisodeManager
from .WindowType import WindowVideo, WindowParameter


class VideoSource:
    def __init__(self):
        """
        Initialize a VideoSource object.
        """
        self.headers: dict[str, str] = {
            'user-agent': get_headers()
        }
        self.is_series: bool = False

    def set_version(self, version: str) -> None:
        """
        Set the version.

        Args:
            version (str): The version to set.
        """
        self.version = version

    def set_domain(self, domain: str) -> None:
        """
        Set the domain.

        Args:
            domain (str): The domain to set.
        """
        self.domain = domain

    def set_url_base_name(self, base_name: str) -> None:
        """
        Set the base url of the site.

        Args:
            domain (str): The url of the site to set.
        """
        self.base_name = base_name

    def set_media_id(self, media_id: str) -> None:
        """
        Set the media ID.

        Args:
            media_id (str): The media ID to set.
        """
        self.media_id = media_id

    def set_series_name(self, series_name: str) -> None:
        """
        Set the series name.

        Args:
            series_name (str): The series name to set.
        """
        self.is_series: bool = True
        self.series_name: str = series_name
        self.obj_title_manager: TitleManager = TitleManager()
        self.obj_episode_manager: EpisodeManager = EpisodeManager()

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

            # Make a request to collect information about seasons
            response = requests.get(f"https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}", headers=self.headers)
            response.raise_for_status()  # Raise exception for non-200 status codes

            if response.ok:

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
            number_season (int): The season number.
        """
        try:

            # Make a request to collect information about a specific season
            response = requests.get(f'https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}/stagione-{number_season}', headers=self.headers)
            response.raise_for_status()  # Raise exception for non-200 status codes

            if response.ok:

                # Extract JSON response if available
                json_response = response.json().get('props', {}).get('loadedSeason', {}).get('episodes', [])
                
                # Iterate over JSON data and add episodes to the manager
                for dict_episode in json_response:
                    self.obj_episode_manager.add_episode(dict_episode)

        except Exception as e:
            logging.error(f"Error collecting title season info: {e}")
            raise
    
    def get_iframe(self, episode_id: str = None) -> None:
        """
        Get iframe source.

        Args:
            episode_id (str): The episode ID, present only for series
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
            response.raise_for_status()  # Raise exception for non-200 status codes

            if response.ok:

                # Parse response with BeautifulSoup to get iframe source
                soup = BeautifulSoup(response.text, "html.parser")
                self.iframe_src: str = soup.find("iframe").get("src")

        except Exception as e:
            logging.error(f"Error getting iframe source: {e}")
            raise

    def parse_script(self, script_text: str) -> None:
        """
        Parse script text.

        Args:
            script_text (str): The script text to parse.
        """
        try:

            # Extract window video and parameter information from script text
            str_window_video = re.search(r"window.video = {.*}", str(script_text)).group()
            str_window_parameter = re.search(r"params: {[\s\S]*}", str(script_text)).group()

            # Fix windos and video parameter
            str_window_video = str_window_video.split(" = ")[1]
            str_window_parameter = str(str_window_parameter.replace("\n", "").replace("  ", "").split(",},")[0] + "}").split("params: ")[1]

            # Create window video and parameter objects
            self.window_video = WindowVideo(data = json.loads(str_window_video.replace("'", '"')))
            self.window_parameter = WindowParameter(data = json.loads(str_window_parameter.replace("'", '"')))

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
                response = requests.get(self.iframe_src, headers=self.headers)
                response.raise_for_status()  # Raise exception for non-200 status codes

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
        try:

            # Generate playlist URL
            query = urlencode(list(self.window_parameter.data.items()))
            base_url = f'https://vixcloud.co/playlist/{self.window_video.id}'

            full_url = urljoin(base_url, '?' + query)

            return full_url
        
        except AttributeError as e:
            logging.error(f"Error getting playlist: {e}")
            raise

    def get_key(self) -> str:
        """
        Get key.

        Returns:
            str: The key content, or None if there's an error.
        """
        try:

            # Fix title for latin-1
            title = quote(self.window_video.name)

            # Set referer header for the request
            self.headers['referer'] = f'https://vixcloud.co/embed/{self.window_video.id}?token={self.window_parameter.token}&title={title}&referer=1&expires={self.window_parameter.expires}&canPlayFHD=1'
            
            # Make a request to get key content
            response = requests.get('https://vixcloud.co/storage/enc.key', headers=self.headers)
            response.raise_for_status()  # Raise exception for non-200 status codes

            if response.ok:

                # Convert key content to hexadecimal format
                hex_content = binascii.hexlify(response.content).decode('utf-8')
                return hex_content
            
        except Exception as e:
            logging.error(f"Error getting key: {e}")
            raise

class VideoSourceAnime(VideoSource):
    """
    A class representing a video source for anime content.
    Inherits from VideoSource class.
    """

    def __init__(self) -> None:
        super().__init__()
        # MEDIA ID IS THE INDEX OF EPISODE

    def collect_episode_info(self) -> None:
        """
        Collects information about the episode.
        """
        try:
            if self.media_id is None:
                raise ValueError("Media ID is not set.")
            
            params = {
                'start_range': self.media_id,
                'end_range': self.media_id + 1
            }

            # series_name is the index of season in this case, index is the index of episode
            response = requests.get(f'https://www.{self.base_name}.{self.domain}/info_api/{self.series_name}/{self.media_id}', params=params)
            if not response.ok:
                return None

            response.raise_for_status()

            # Get last episode in json request
            json_response = response.json()['episodes'][-1]

            # Add in array of episode ( only one is store )
            self.obj_episode_manager.add_episode(json_response)
        
        except Exception as e:
            logging.error(f"An error occurred while collecting episode info: {e}")
            raise

    def get_embed(self) ->str:
        """
        Retrieves the embed URL for the episode.
        """
        try:
            if not self.obj_episode_manager.episodes:
                raise ValueError("No episodes available.")

            # Make request to get vixcloud embed url
            embed_url_response = requests.get(f'https:///www.{self.base_name}.{self.domain}/embed-url/{self.obj_episode_manager.episodes[0].id}')
            if not embed_url_response.ok:
                return None

            embed_url_response.raise_for_status()

            # Make request to embed url to get video paramter text
            embed_url = requests.get(embed_url_response.text).text
            
            # Parse script to get video information
            self.parse_script(script_text=embed_url)
        
        except Exception as e:
            logging.error(f"An error occurred while getting embed URL: {e}")
            raise