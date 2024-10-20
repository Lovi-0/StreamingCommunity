# 3.12.23

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Lib.Downloader import HLS_Downloader


# Logic class
from .Core.Player.vixcloud import VideoSource
from ..Template.Class.SearchType import MediaItem


# Variable
from .costant import ROOT_PATH, SITE_NAME, MOVIE_FOLDER
video_source = VideoSource()
        

def download_film(select_title: MediaItem, domain: str,  version: str):
    """
    Downloads a film using the provided film ID, title name, and domain.

    Parameters:
        - domain (str): The domain of the site
        - version (str): Version of site.
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{select_title.slug} \n")

    # Set domain and media ID for the video source
    video_source.setup(version, domain, select_title.id)

    # Retrieve scws and if available master playlist
    video_source.get_iframe()
    video_source.get_content()
    master_playlist = video_source.get_playlist()

    # Define the filename and path for the downloaded film
    mp4_format = (select_title.slug) + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, select_title.slug)

    # Download the film using the m3u8 playlist, and output filename
    HLS_Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_format)
    ).start()
