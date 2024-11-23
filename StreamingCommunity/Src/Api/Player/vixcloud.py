# 01.03.24

import sys
import logging
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Util.console import console, Panel
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from .Helper.Vixcloud.util import Episode, EpisodeManager, Season, SeasonManager, WindowVideo, WindowParameter, DynamicJSONConverter


# Variable
max_timeout = config_manager.get_int("REQUESTS", "timeout")



class VideoSource:
    def __init__(self, site_name: str):
        """
        Initialize a VideoSource object.
        """
        self.headers = {'user-agent': get_headers()}
        self.is_series = False
        self.base_name = site_name

    def setup(self, version: str = None, domain: str = None, media_id: int = None, series_name: str = None):
        """
        Set up the class

        Parameters:
            - version (str): The version to set.
            - media_id (int): The media ID to set.
            - series_name (str): The series name to set.
        """
        self.version = version
        self.domain = domain
        self.media_id = media_id

        if series_name is not None:
            self.is_series = True
            self.series_name = series_name
            self.obj_season_manager: SeasonManager = SeasonManager()
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

            response = httpx.get(
                url=f"https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}", 
                headers=self.headers, 
                timeout=max_timeout
            )
            response.raise_for_status()

            # Extract JSON response if available
            json_response = response.json().get('props', {}).get('title', {}).get('seasons', [])
                
            # Iterate over JSON data and add titles to the manager
            for dict_season in json_response:
                self.obj_season_manager.add_season(dict_season)

        except Exception as e:
            logging.error(f"Error collecting season info: {e}")
            raise

    def collect_title_season(self, number_season: int) -> None:
        """
        Collect information about a specific season.

        Parameters:
            - number_season (int): The season number.
        """
        try:

            # Make a request to collect information about a specific season
            response = httpx.get(
                url=f'https://{self.base_name}.{self.domain}/titles/{self.media_id}-{self.series_name}/stagione-{number_season}', 
                headers=self.headers, 
                timeout=max_timeout
            )
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

        Parameters:
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
            response = httpx.get(
                url=f"https://{self.base_name}.{self.domain}/iframe/{self.media_id}", 
                params=params, 
                timeout=max_timeout
            )
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

        Parameters:
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
                    response = httpx.get(
                        url=self.iframe_src, 
                        headers=self.headers, 
                        timeout=max_timeout
                    )
                    response.raise_for_status()

                except Exception as e:
                    print("\n")
                    console.print(Panel("[red bold]Coming soon", title="Notification", title_align="left", border_style="yellow"))
                    sys.exit(0)

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


class AnimeVideoSource(VideoSource):
    def __init__(self, site_name: str):
        """
        Initialize a VideoSource object.
        """
        self.headers = {'user-agent': get_headers()}
        self.is_series = False
        self.base_name = site_name
        self.domain = config_manager.get_dict('SITE', self.base_name)['domain']

    def setup(self, media_id: int = None, series_name: str = None):
        """
        Set up the class

        Parameters:
            - media_id (int): The media ID to set.
            - series_name (str): The series name to set.
        """
        self.media_id = media_id

        if series_name is not None:
            self.is_series = True
            self.series_name = series_name
            self.obj_episode_manager: EpisodeManager = EpisodeManager()
            
    def get_count_episodes(self):
        """
        Fetches the total count of episodes available for the anime.
        
        Returns:
            - int or None: Total count of episodes if successful, otherwise None.
        """
        try:

            response = httpx.get(
                url=f"https://www.{self.base_name}.{self.domain}/info_api/{self.media_id}/", 
                headers=self.headers, 
                timeout=max_timeout
            )
            response.raise_for_status()

            # Parse JSON response and return episode count
            return response.json()["episodes_count"]
        
        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching episode count: {e}")
            return None
    
    def get_info_episode(self, index_ep: int) -> Episode:
        """
        Fetches information about a specific episode.
        
        Parameters:
            - index_ep (int): Index of the episode.
            
        Returns:
            - obj Episode or None: Information about the episode if successful, otherwise None.
        """
        try:

            params = {
                "start_range": index_ep, 
                "end_range": index_ep + 1
            }

            response = httpx.get(
                url=f"https://www.{self.base_name}.{self.domain}/info_api/{self.media_id}/{index_ep}", 
                headers=self.headers, 
                params=params, 
                timeout=max_timeout
            )
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
        
        Parameters:
            - episode_id (int): ID of the episode.
            
        Returns:
            - str or None: Script successful, otherwise None.
        """
        try:

            response = httpx.get(
                url=f"https://www.{self.base_name}.{self.domain}/embed-url/{episode_id}", 
                headers=self.headers, 
                timeout=max_timeout
            )
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
            self.src_mp4 = soup.find("body").find_all("script")[1].text.split(" = ")[1].replace("'", "")

            return script
        
        except Exception as e:
            logging.error(f"(EpisodeDownloader) Error fetching embed URL: {e}")
            return None
