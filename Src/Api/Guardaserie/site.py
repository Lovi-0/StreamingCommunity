# 09.06.24

import os
import sys
import logging
from urllib.parse import urlparse


# External libraries
import requests


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.os import create_folder, can_create_file
from Src.Util._jsonConfig import config_manager
from Src.Util.headers import get_headers
from Src.Lib.Hls.downloader import Downloader


# Logic class
from .Core.Player.supervideo import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
from .costant import MAIN_FOLDER, MOVIE_FOLDER


def title_search() -> int:
    """
    Search for titles based on a search query.
    """

    print()
    url_search = msg.ask(f"[cyan]Insert url title")

    # Send request to search for titles
    response = requests.get(url_search, headers={'user-agent': get_headers()})
    response.raise_for_status()

    # Get playlist
    video_source = VideoSource()
    video_source.setup(url_search)

    
    parsed_url = urlparse(url_search)
    path_parts = parsed_url.path.split('/')
    mp4_name = path_parts[-2] if path_parts[-1] == '' else path_parts[-1] + ".mp4"

    # Create destination folder
    mp4_path = os.path.join(ROOT_PATH, MAIN_FOLDER, MOVIE_FOLDER)

    # Check if can create file output
    create_folder(mp4_path)                                                                    
    if not can_create_file(mp4_name):  
        logging.error("Invalid mp4 name.")
        sys.exit(0)


    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()