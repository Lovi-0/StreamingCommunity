# 03.07.24

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Lib.Downloader import HLS_Downloader


# Logic class
from ..Template.Class.SearchType import MediaItem
from .Player.maxstream import VideoSource


# Config
from .costant import ROOT_PATH, SITE_NAME, MOVIE_FOLDER


def download_film(select_title: MediaItem):
    """
    Downloads a film using the provided obj.

    Parameters:
        - select_title (MediaItem): The media item to be downloaded. This should be an instance of the MediaItem class, containing attributes like `name` and `url`.
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{select_title.name} \n")

    # Setup api manger
    video_source = VideoSource(select_title.url)

    # Define output path
    mp4_name = select_title.name +".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, select_title.name)

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    HLS_Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()
