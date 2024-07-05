# 26.05.24

import os
import sys
import logging


# Internal utilities
from Src.Util.message import start_message
from Src.Util.console import console
from Src.Util.os import create_folder, can_create_file
from Src.Lib.Downloader import HLS_Downloader


# Logic class
from .Core.Player.supervideo import VideoSource


# Config
from .costant import ROOT_PATH, SITE_NAME, MOVIE_FOLDER

  

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
    video_source = VideoSource(url)

    # Define output path
    mp4_name = str(title_name).replace("-", "_") + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, title_name)

    # Ensure the folder path exists
    create_folder(mp4_path)
    
    # Check if the MP4 file can be created
    if not can_create_file(mp4_name):
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    HLS_Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()