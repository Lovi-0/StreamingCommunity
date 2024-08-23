# 23.08.24

# 3.12.23

import os
import sys
import logging
from urllib.parse import urlparse


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Util.os import create_folder, remove_special_characters
from Src.Lib.Downloader import MP4_downloader


# Logic class
from .Core.Player.driveleech import DownloadAutomation


# Variable
from .costant import ROOT_PATH, SITE_NAME, MOVIE_FOLDER
        

def download_film(name: str, url: str):
    """
    Downloads a film using the provided url.

    Parameters:
        - name (str): Name of the film
        - url (str): MP4 url of the film
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{name} \n")

    # Construct the MP4 file name and path
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, remove_special_characters(name))

    # Ensure the folder path exists
    create_folder(mp4_path)

    # Parse start page url
    downloder_vario = DownloadAutomation(url)
    downloder_vario.run()
    downloder_vario.quit()

    # Parse mp4 link
    mp4_final_url = downloder_vario.mp4_link
    parsed_url = urlparse(mp4_final_url)

    MP4_downloader(
        url = mp4_final_url, 
        path = os.path.join(mp4_path, "film_0.mp4"),
        referer = f"{parsed_url.scheme}://{parsed_url.netloc}/",
    )