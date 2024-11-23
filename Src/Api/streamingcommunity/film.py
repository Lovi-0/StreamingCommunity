# 3.12.23

import os
import time


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.os import os_manager
from Src.Util.message import start_message
from Src.Util.call_stack import get_call_stack
from Src.Lib.Downloader import HLS_Downloader
from ..Template import execute_search


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
    title_name = os_manager.get_sanitize_file(select_title.slug) + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, select_title.slug)

    # Download the film using the m3u8 playlist, and output filename
    r_proc = HLS_Downloader(
        m3u8_playlist=master_playlist, 
        output_filename=os.path.join(mp4_path, title_name)
    ).start()

    if r_proc == 404:
        time.sleep(2)

        # Re call search function
        if msg.ask("[green]Do you want to continue [white]([red]y[white])[green] or return at home[white]([red]n[white]) ", choices=['y', 'n'], default='y', show_choices=True) == "n":
            frames = get_call_stack()
            execute_search(frames[-4])

    if r_proc != None:
        console.print("[green]Result: ")
        console.print(r_proc)
