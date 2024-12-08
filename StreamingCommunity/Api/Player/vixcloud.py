# 01.03.24

import sys
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console, Panel
from StreamingCommunity.Util._jsonConfig import config_manager
from .Helper.Vixcloud.util import WindowVideo, WindowParameter, StreamsCollection
from .Helper.Vixcloud.js_parser import JavaScriptParser


# Variable
max_timeout = config_manager.get_int("REQUESTS", "timeout")


class VideoSource:
    def __init__(self, site_name: str,  is_series: bool):
        """
        Initialize video source for streaming site.
        
        Args:
            site_name (str): Name of streaming site
            is_series (bool): Flag for series or movie content
        """
        self.headers = {'user-agent': get_headers()}
        self.base_name = site_name
        self.domain = config_manager.get_dict('SITE', self.base_name)['domain']
        self.is_series = is_series

    def setup(self, media_id: int):
        """
        Configure media-specific context.
        
        Args:
            media_id (int): Unique identifier for media item
        """
        self.media_id = media_id

    def get_iframe(self, episode_id: int) -> None:
        """
        Retrieve iframe source for specified episode.
        
        Args:
            episode_id (int): Unique identifier for episode
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
        Convert raw script to structured video metadata.
        
        Args:
            script_text (str): Raw JavaScript/HTML script content
        """
        try:
            converter = JavaScriptParser.parse(js_string=str(script_text))

            # Create window video, streams and parameter objects
            self.canPlayFHD = bool(converter.get('canPlayFHD'))
            self.window_video = WindowVideo(converter.get('video'))
            self.window_streams = StreamsCollection(converter.get('streams'))
            self.window_parameter = WindowParameter(converter.get('masterPlaylist'))

        except Exception as e:
            logging.error(f"Error parsing script: {e}")
            raise

    def get_content(self) -> None:
        """
        Fetch and process video content from iframe source.
        
        Workflow:
            - Validate iframe source
            - Retrieve content
            - Parse embedded script
        """
        try:
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
        Generate authenticated playlist URL.

        Returns:
            str: Fully constructed playlist URL with authentication parameters
        """
        # Initialize parameters dictionary
        params = {}

        # Add 'h' parameter if video quality is 1080p
        if self.canPlayFHD:
            params['h'] = 1

        # Parse the original URL
        parsed_url = urlparse(self.window_parameter.url)
        query_params = parse_qs(parsed_url.query)

        # Check specifically for 'b=1' in the query parameters
        if 'b' in query_params and query_params['b'] == ['1']:
            params['b'] = 1

        # Add authentication parameters (token and expiration)
        params.update({
            "token": self.window_parameter.token,
            "expires": self.window_parameter.expires
        })

        # Build the updated query string
        query_string = urlencode(params)

        # Construct the new URL with updated query parameters
        return urlunparse(parsed_url._replace(query=query_string))

    def get_mp4(self, url_to_download: str, scws_id: str) -> list:
        """
        Generate download links for the specified resolutions from StreamingCommunity.
        
        Args:
            url_to_download (str): URL of the video page.
            scws_id (str): SCWS ID of the title.
        
        Returns:
            list: A list of video download URLs.
        """
        headers = {
            'referer': url_to_download,
            'user-agent': get_headers(),
        }

        # API request to get video details
        video_api_url = f'https://{self.base_name}.{self.domain}/api/video/{scws_id}'
        response = httpx.get(video_api_url, headers=headers)

        if response.status_code == 200:
            response_json = response.json()

            video_tracks = response_json.get('video_tracks', [])
            track = video_tracks[-1]
            console.print(f"[cyan]Available resolutions: [red]{[str(track['quality']) for track in video_tracks]}")

            # Request download link generation for each track
            download_response = httpx.post(
                url=f'https://{self.base_name}.{self.domain}/api/download/generate_link?scws_id={track["video_id"]}&rendition={track["quality"]}',
                headers={
                    'referer': url_to_download,
                    'user-agent': get_headers(),
                    'x-xsrf-token': config_manager.get("SITE", self.base_name)['extra']['x-xsrf-token']
                },
                cookies={
                    'streamingcommunity_session': config_manager.get("SITE", self.base_name)['extra']['streamingcommunity_session']
                }
            )

            if download_response.status_code == 200:
                return {'url': download_response.text, 'quality': track["quality"]}

            else:
                logging.error(f"Failed to generate link for resolution {track['quality']} (HTTP {download_response.status_code}).")

        else:
            logging.error(f"Error fetching video API URL (HTTP {response.status_code}).")
            return []


class VideoSourceAnime(VideoSource):
    def __init__(self, site_name: str):
        """
        Initialize anime-specific video source.
        
        Args:
            site_name (str): Name of anime streaming site
        
        Extends base VideoSource with anime-specific initialization
        """
        self.headers = {'user-agent': get_headers()}
        self.base_name = site_name
        self.domain = config_manager.get_dict('SITE', self.base_name)['domain']
        self.src_mp4 = None

    def get_embed(self, episode_id: int):
        """
        Retrieve embed URL and extract video source.
        
        Args:
            episode_id (int): Unique identifier for episode
        
        Returns:
            str: Parsed script content
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
            logging.error(f"Error fetching embed URL: {e}")
            return None