# 01.07.24

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Util.os import create_folder, can_create_file, remove_special_characters
from Src.Lib.Downloader import TOR_downloader


# Logic class
from ..Template.Class.SearchType import MediaItem


# Config
from .costant import ROOT_PATH, SITE_NAME, MOVIE_FOLDER


def download_title(select_title: MediaItem):
    """
    Downloads a media item and saves it as an MP4 file.

    Parameters:
        - select_title (MediaItem): The media item to be downloaded. This should be an instance of the MediaItem class, containing attributes like `name` and `url`.
    """

    start_message()

    console.print(f"[yellow]Download:  [red]{select_title.name} \n")
    print()

    # Define output path
    title_name = remove_special_characters(select_title.name)
    mp4_name = title_name.replace("-", "_") + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, remove_special_characters(title_name.replace(".mp4", "")))
    
    # Check if can create file output
    create_folder(mp4_path)                                                                    
    if not can_create_file(mp4_name):  
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Tor manager
    manager = TOR_downloader()
    manager.add_magnet_link(select_title.url)
    manager.start_download()
    manager.move_downloaded_files(mp4_path)