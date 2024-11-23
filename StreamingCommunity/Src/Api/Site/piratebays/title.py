# 02.07.24

import os
import sys


# Internal utilities
from StreamingCommunity.Src.Util.console import console
from StreamingCommunity.Src.Util.message import start_message
from StreamingCommunity.Src.Util.os import os_manager
from StreamingCommunity.Src.Lib.Downloader import TOR_downloader


# Logic class
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaItem


# Config
from .costant import ROOT_PATH, DOMAIN_NOW, SITE_NAME, MOVIE_FOLDER


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
    title_name = os_manager.get_sanitize_file(select_title.name.replace("-", "_") + ".mp4")
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, title_name.replace(".mp4", ""))
    
    # Create output folder
    os_manager.create_path(mp4_path)   

    # Tor manager
    manager = TOR_downloader()
    manager.add_magnet_link(select_title.url)
    manager.start_download()
    manager.move_downloaded_files(mp4_path)
