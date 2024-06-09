# 26.05.24

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager
from Src.Lib.Hls.downloader import Downloader
from Src.Util.message import start_message


# Logic class
from .Core.Player.supervideo import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
from .costant import MAIN_FOLDER, MOVIE_FOLDER


# Variable
video_source = VideoSource()
        

def download_film(title_name: str, url: str):
    """
    Downloads a film using the provided film ID, title name, and domain.

    Args:
        - title_name (str): The name of the film title.
        - url (str): The url of the video
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{title_name} \n")

    # Set domain and media ID for the video source
    video_source.setup(
        url = url
    )

    # Define output path
    mp4_name = str(title_name).replace("-", "_") + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, MAIN_FOLDER, MOVIE_FOLDER, title_name)

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, key, and output filename
    Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()