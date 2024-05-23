# 3.12.23

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager
from Src.Lib.Hls.downloader import Downloader
from Src.Util.file_validator import can_create_file
from Src.Util.message import start_message
from Src.Util.os import remove_special_characters
from Src.Lib.Unidecode import transliterate


# Logic class
from .Core.Vix_player.player import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
STREAMING_FOLDER = config_manager.get('SITE', 'streaming_site_name')


# Variable
video_source = VideoSource()
        

def download_film(id_film: str, title_name: str, domain: str):
    """
    Downloads a film using the provided film ID, title name, and domain.

    Args:
        - id_film (str): The ID of the film.
        - title_name (str): The name of the film title.
        - domain (str): The domain of the site
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{title_name} \n")

    # Set domain and media ID for the video source
    video_source.setup(
        domain = domain,
        media_id = id_film
    )

    # Retrieve scws and if available master playlist
    video_source.get_iframe()
    video_source.get_content()
    master_playlist = video_source.get_playlist()


    # Define the filename and path for the downloaded film
    mp4_name = title_name.replace("-", "_")
    mp4_format = remove_special_characters(transliterate(mp4_name) + ".mp4")

    if not can_create_file(mp4_format):
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Download the film using the m3u8 playlist, key, and output filename
    Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(ROOT_PATH, STREAMING_FOLDER, "Movie", title_name, mp4_format)
    ).start()