# 29.06.24

import os
import sys
import logging
from urllib.parse import urlparse


# Internal utilities
from Src.Util.message import start_message
from Src.Util.os import create_folder, can_create_file
from Src.Lib.Downloader import MP4_downloader


# Logic class
from .Player.lonelil import ApiManager
from ..Template.Class.SearchType import MediaItem
from Src.Lib.Driver import WebAutomation


# Variable
from .costant import ROOT_PATH, SITE_NAME, SERIES_FOLDER


def download_film(media: MediaItem, main_driver: WebAutomation):
    """
    Downloads a media title using its API manager and WebAutomation driver.

    Parameters:
        - media (MediaItem): The media item to be downloaded.
        - main_driver (WebAutomation): The web automation driver instance.
    """

    start_message()
    
    # Initialize the API manager with the media and driver
    api_manager = ApiManager(media, main_driver)
    
    # Get the URL of the media playlist
    url_playlist = api_manager.get_playlist()

    # Construct the MP4 file name and path
    mp4_name = str(media.name).replace("-", "_") + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, SERIES_FOLDER, media.name)

    # Ensure the folder path exists
    create_folder(mp4_path)

    # Check if the MP4 file can be created
    if not can_create_file(mp4_name):
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Parse the URL of the playlist
    parsed_url = urlparse(url_playlist)

    # Quit the main driver instance
    main_driver.quit()

    # Initiate the MP4 downloader with necessary parameters
    MP4_downloader(
        url=url_playlist,
        path=os.path.join(mp4_path, mp4_name),
        referer=f"{parsed_url.scheme}://{parsed_url.netloc}/",
    )
