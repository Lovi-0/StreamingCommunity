# 3.12.23 -> 10.12.23

import os
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util.config import config_manager
from Src.Lib.FFmpeg.my_m3u8 import Downloader
from Src.Util.message import start_message
from .Class import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
MOVIE_FOLDER = config_manager.get('DEFAULT', 'movies_folder_name')
STREAM_SITE_NAME = config_manager.get('SITE', 'streaming_site_name')


# Variable
video_source = VideoSource()
video_source.set_url_base_name(STREAM_SITE_NAME)
        

def download_film(id_film: str, title_name: str, domain: str):
    """
    Downloads a film using the provided film ID, title name, and domain.

    Args:
        id_film (str): The ID of the film.
        title_name (str): The name of the film title.
        domain (str): The domain of the site
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{title_name} \n")

    # Set domain and media ID for the video source
    video_source.set_domain(domain)
    video_source.set_media_id(id_film)

    # Retrieve the iframe and content for the video source
    video_source.get_iframe()
    video_source.get_content()

    # Define the filename and path for the downloaded film
    mp4_name = title_name.replace("-", "_")
    mp4_format = mp4_name + ".mp4"

    # Download the film using the m3u8 playlist, key, and output filename
    try:
        obj_download = Downloader(
            m3u8_playlist = video_source.get_playlist(),
            key = video_source.get_key(),
            output_filename = os.path.join(ROOT_PATH, MOVIE_FOLDER, title_name, mp4_format)
        )

        obj_download.download_m3u8()

    except Exception as e:
        logging.error(f"(download_film) Error downloading film: {e}")
        pass
