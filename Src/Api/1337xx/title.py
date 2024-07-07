# 02.07.24

import os
import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Util.headers import get_headers
from Src.Util.os import create_folder, can_create_file, remove_special_characters
from Src.Lib.Downloader import TOR_downloader


# Logic class
from ..Template.Class.SearchType import MediaItem


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
    title_name = remove_special_characters(select_title.name)
    mp4_name = title_name.replace("-", "_") + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, remove_special_characters(title_name.replace(".mp4", "")))
    
    # Check if can create file output
    create_folder(mp4_path)                                                                    
    if not can_create_file(mp4_name):  
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Make request to page with magnet
    full_site_name = f"{SITE_NAME}.{DOMAIN_NOW}"
    response = httpx.get("https://" + full_site_name + select_title.url, headers={'user-agent': get_headers()}, follow_redirects=True)

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    final_url = soup.find("a", class_="torrentdown1").get("href")

    # Tor manager
    manager = TOR_downloader()
    manager.add_magnet_link(final_url)
    manager.start_download()
    manager.move_downloaded_files(mp4_path)